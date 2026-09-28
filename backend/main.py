import logging
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import BadRequestError, RateLimitError
from pydantic import BaseModel, Field, field_validator

from document_service import MAX_PDF_BYTES, ingest_pdf
from rag_service import answer_question

logger = logging.getLogger(__name__)
app = FastAPI(title="PDF Research Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    previous_response_id: str | None = Field(default=None, max_length=200)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question cannot be blank.")
        return value.strip()


class Source(BaseModel):
    document_id: str
    document_title: str
    chunk_index: int
    content: str
    similarity: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    response_id: str | None


def service_error(exc: Exception) -> HTTPException:
    # Never expose upstream errors, credentials, or document contents to clients.
    logger.error("Upstream request failed (%s)", type(exc).__name__)
    if isinstance(exc, RateLimitError):
        return HTTPException(429, "OpenAI rate or usage limit reached. Check billing or try again later.")
    if isinstance(exc, BadRequestError):
        return HTTPException(400, "OpenAI rejected the request. Start a new chat if conversation context has expired, and check the backend model configuration.")
    return HTTPException(502, "Document or AI service is unavailable. Check backend configuration and the Supabase migration, then retry.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        return answer_question(request.question, request.previous_response_id)
    except Exception as exc:
        raise service_error(exc) from exc


@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)):
    try:
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(400, "Select a PDF file.")
        file_bytes = file.file.read(MAX_PDF_BYTES + 1)
        if len(file_bytes) > MAX_PDF_BYTES:
            raise HTTPException(413, "PDF must be 20 MB or smaller.")
        return ingest_pdf(file_bytes, file.filename or "document.pdf")
    except HTTPException:
        raise
    except Exception as exc:
        raise service_error(exc) from exc
    finally:
        file.file.close()
