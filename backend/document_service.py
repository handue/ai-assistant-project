import hashlib
import logging
from io import BytesIO
from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import HTTPException
from postgrest.exceptions import APIError
from pypdf import PdfReader

from ai_client import create_embeddings
from supabase_client import supabase

logger = logging.getLogger(__name__)
MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_TEXT_CHARACTERS = 500_000


def extract_pdf_text(file_bytes: bytes) -> str:
    pdf = PdfReader(BytesIO(file_bytes))
    if pdf.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported.")
    pages = []
    length = 0
    for page in pdf.pages:
        text = page.extract_text() or ""
        length += len(text)
        if length > MAX_TEXT_CHARACTERS:
            raise ValueError("PDF has too much text; upload a smaller document.")
        pages.append(text)
    return "\n\n".join(pages).strip()


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    if chunk_size <= 0 or not 0 <= overlap < chunk_size:
        raise ValueError("Chunk overlap must be smaller than the positive chunk size.")
    return [chunk for start in range(0, len(text), chunk_size - overlap)
            if (chunk := text[start : start + chunk_size].strip())]


def ingest_pdf(file_bytes: bytes, filename: str) -> dict:
    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(400, "Only valid PDF files are allowed.")
    content_hash = hashlib.sha256(file_bytes).hexdigest()
    existing = supabase.table("documents").select("*").eq("content_hash", content_hash).execute().data
    if existing:
        if existing[0]["ingestion_status"] != "ready":
            raise HTTPException(409, "This PDF is already being processed. Try again shortly.")
        count = supabase.table("document_chunks").select("id", count="exact", head=True).eq("document_id", existing[0]["id"]).execute().count
        return {"document": existing[0], "chunk_count": count, "duplicate": True}

    try:
        text = extract_pdf_text(file_bytes)
    except Exception as exc:
        detail = str(exc) if isinstance(exc, ValueError) else "PDF could not be read. Use an unencrypted, valid PDF."
        raise HTTPException(422, detail) from exc
    if not text:
        raise HTTPException(422, "PDF contains no extractable text. Scanned PDFs need OCR before upload.")
    chunks = chunk_text(text)
    document_id = str(uuid4())
    filename = PurePosixPath(filename.replace("\\", "/")).name or "document.pdf"
    storage_path = f"{document_id}/document.pdf"
    try:
        document = supabase.table("documents").insert({
            "id": document_id, "title": filename, "original_filename": filename,
            "storage_path": storage_path, "mime_type": "application/pdf",
            "content_hash": content_hash, "ingestion_status": "processing",
        }).execute().data[0]
    except APIError as exc:
        if exc.code == "23505":
            raise HTTPException(409, "This PDF was uploaded concurrently. Try again shortly.") from exc
        raise

    # Reserve the hash before external work. Only ready documents are searchable.
    try:
        supabase.storage.from_("documents").upload(
            storage_path, file_bytes, {"content-type": "application/pdf", "upsert": "false"},
        )
        embeddings = create_embeddings(chunks)
        for start in range(0, len(chunks), 64):
            supabase.table("document_chunks").insert([
                {"document_id": document_id, "chunk_index": index,
                 "content": chunks[index], "embedding": embeddings[index]}
                for index in range(start, min(start + 64, len(chunks)))
            ]).execute()
        document = supabase.table("documents").update({"ingestion_status": "ready"}).eq("id", document_id).execute().data[0]
    except Exception:
        # Storage and PostgreSQL cannot share a transaction. Compensate on failure.
        for cleanup in (
            lambda: supabase.table("document_chunks").delete().eq("document_id", document_id).execute(),
            lambda: supabase.table("documents").delete().eq("id", document_id).execute(),
            lambda: supabase.storage.from_("documents").remove([storage_path]),
        ):
            try:
                cleanup()
            except Exception as cleanup_error:
                logger.error("Ingestion cleanup failed for %s (%s)", document_id, type(cleanup_error).__name__)
        raise
    return {"document": document, "text_length": len(text), "chunk_count": len(chunks), "duplicate": False}
