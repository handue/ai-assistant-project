# PDF Research Assistant — RAG MVP

Upload a text PDF, ask questions, and inspect the document excerpts used for each answer.
A minimal portfolio project with multi-turn conversation context and no authentication, streaming, agents, or conversation database.

## Architecture

- **Frontend:** Next.js App Router, React, TypeScript, Tailwind CSS. TanStack Query manages question/upload mutations; Zustand holds chat messages, sources, and OpenAI response IDs in browser memory.
- **Backend:** FastAPI, Pydantic, pypdf, OpenAI Python SDK, Supabase Python SDK.
- **AI:** OpenAI Responses API for answers; `text-embedding-3-small` with 1536 dimensions for both documents and questions.
- **Persistence:** Supabase PostgreSQL stores document metadata and chunks; pgvector performs cosine search. A private Supabase Storage bucket stores original PDFs.

```text
PDF selection → POST /documents/upload
  → validate PDF → extract text → 1200-character chunks (200-character overlap)
  → reserve SHA-256 hash → Supabase Storage
  → batch embeddings → document_chunks.embedding → mark document ready

Question → POST /ask → question embedding
  → match_document_chunks RPC (top 5, cosine similarity ≥ 0.3)
  → numbered retrieved excerpts + question → OpenAI Responses API
  → answer + sources + response_id → Next.js chat and source previews
```

`main.py` handles HTTP validation and errors. `document_service.py` handles ingestion and cleanup. `ai_client.py` shares the OpenAI client and embedding configuration. `rag_service.py` handles retrieval, context assembly, and grounded generation. `supabase_client.py` provides the backend-only database/storage client.

Every answer request supplies grounding instructions again and retrieves fresh context. Prior OpenAI responses help interpret conversation context; current retrieved excerpts are the factual evidence. If no excerpts meet the threshold, the backend returns an insufficient-information answer with no sources and skips answer generation. Sources are retrieved evidence, not a guarantee that every excerpt was cited by the model.

## Setup

Use Python 3.11+ and a Node.js version supported by the installed Next.js (Node 20.9+). You need OpenAI API access and a Supabase project.

### 1. Supabase (manual)

Run [supabase/migrations/202609280001_rag.sql](supabase/migrations/202609280001_rag.sql) in your project's SQL editor. It creates missing document tables, adds `content_hash` and `ingestion_status`, enables pgvector/RLS, adds unique indexes, creates the cosine-search RPC, and creates the private `documents` bucket if absent. Existing rows are preserved. The RPC uses `1 - cosine distance` for similarity and orders by ascending cosine distance. Exact search keeps this small corpus simple.

The backend requires a Supabase **secret key or legacy service-role key**; a browser/anonymous key cannot perform these operations. The search function is callable only by the service role.

If the migration reports duplicate `(document_id, chunk_index)` values, inspect and resolve those existing duplicate rows before rerunning; the migration deliberately does not delete existing data. If a `match_document_chunks` function already exists with a different signature/return type, review that function before replacing it.

Old chunks without embeddings are excluded from retrieval. Re-upload old PDFs through the completed ingestion flow to index them. Old document rows have no content hash, so the first re-upload of a legacy PDF can create a new document; subsequent byte-identical uploads reuse it. Similar text in different PDF files is not deduplicated.

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Use your existing `backend/.env`, or create one with these backend-only settings:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your_backend_secret_or_service_role_key
FRONTEND_ORIGIN=http://localhost:3000
```

Keep the existing answer model if already configured. Keep the same embedding model and dimensions for ingestion and retrieval; changing the embedding model requires reindexing the corpus.

```bash
python -m uvicorn main:app --reload
```

API: http://localhost:8000 · Interactive docs: http://localhost:8000/docs.
`GET /health` checks that the application runs; it does not check upstream credentials/services.

### 3. Frontend

In a separate terminal:

```bash
cd frontend
npm ci
npm run dev
```

Use your existing `frontend/.env`, or create one containing only `NEXT_PUBLIC_API_URL=http://localhost:8000`.
Open http://localhost:3000. Secrets belong exclusively in `backend/.env`. Avoid conflicting values across `.env` and `.env.local`.

## API

- `POST /documents/upload`: multipart form field `file`; returns `document`, `chunk_count`, and `duplicate`. A new upload also returns `text_length`. Success means every chunk has an embedding and the document is ready for search.
- `POST /ask`: JSON `{ "question": "What is the reported revenue?", "previous_response_id": null }`.

Example answer (chunk indexes start at zero; citation numbers start at one):

```json
{
  "answer": "Reported revenue was 42 million dollars [1].",
  "response_id": "resp_...",
  "sources": [
    {
      "document_id": "document-uuid",
      "document_title": "annual-report.pdf",
      "chunk_index": 0,
      "content": "Reported revenue was 42 million dollars...",
      "similarity": 0.82
    }
  ]
}
```

Pass the returned `response_id` for follow-ups. It can be null when no context has been generated. The frontend handles this and provides **New chat** to reset conversation context.

## Manual end-to-end test

1. Apply the SQL migration, fill backend environment values, and start both servers.
2. Upload a text PDF containing a recognizable fact (for example, a company and its annual revenue). Wait for **Ready: … (N chunks)**.
3. In Supabase, check the original PDF in the private `documents` bucket, a `documents` row with `ingestion_status = ready` and a content hash, and ordered `document_chunks` rows with non-null 1536-dimensional embeddings.
4. Ask an explicit question about that fact. Confirm the answer references `[1]` and the Sources section shows the filename, chunk index, similarity, preview, and expandable full excerpt/document ID.
5. Ask a follow-up mentioning the company/topic. Confirm chat context continues and each answer has its own sources. Retrieval embeds the current question, so explicit follow-ups work better than vague pronouns.
6. Upload the identical PDF again. Confirm **Already indexed**, the same document ID, and no new document/chunk rows.
7. Ask something unrelated, or ask before uploading in a fresh project. Confirm an insufficient-information response, not an invented answer.
8. Try a non-PDF, a corrupt PDF, and an image-only PDF. Confirm clear error messages. Use **New chat** to reset context; refreshing clears all local chat history.

For a database check in the Supabase SQL editor:

```sql
select d.title, d.ingestion_status, c.chunk_index,
       vector_dims(c.embedding) as dimensions
from public.documents d
join public.document_chunks c on c.document_id = d.id
order by d.created_at desc, c.chunk_index;
```

## Local verification

No network/API calls are made by these tests:

```bash
# From the repository root, after installing backend dependencies:
backend/.venv/bin/python -m unittest discover -s backend/tests -v

cd frontend
npm run lint
npm run build
```

The backend suite uses real multipart FastAPI requests and PDF extraction/chunking, with in-memory Supabase/Storage and mocked OpenAI. It checks ingestion, 1536-dimensional vectors, retrieval/context/source contracts, multi-turn IDs, duplicate handling, failed-ingestion cleanup, invalid/empty PDFs, no-match answers, and rate-limit errors. It does **not** validate the deployed SQL function or real OpenAI answers; run the manual flow for live integration.

## MVP limits and error recovery

- Text PDFs only (no OCR), up to 20 MB and 500,000 extracted characters. Indexing is synchronous; keep PDFs reasonably small.
- Duplicate protection uses a SHA-256 file hash and a unique database index. Concurrent uploads return a retryable conflict. Chunks are uniquely indexed by document and chunk index.
- Only ready documents are retrieved. Failed ingestion attempts remove their metadata, chunks, and Storage object where possible. Storage and database operations cannot share one transaction. A process crash can leave a `processing` document; inspect/remove that incomplete upload in Supabase before retrying. Cleanup failures are logged with the document ID.
- Cosine similarity is a relevance score, not confidence or a percentage. The fixed 0.3 threshold is a simple starting point.
- Chunking uses characters and can split sentences. Multi-turn context is managed by OpenAI response IDs, with no persistent conversation tables in use. The current-question embedding can miss context in vague follow-ups.
- This MVP has no authentication and searches a shared corpus. Run locally for a portfolio demo; do not expose an unrestricted backend publicly.
- `.env`, `.venv`, `node_modules`, build artifacts, and Python bytecode are ignored. Local environment files are not committed.

## 한국어

PDF 업로드부터 근거 기반 답변과 출처 표시까지 연결한 최소 RAG MVP입니다.
Next.js/TypeScript 프론트엔드는 TanStack Query로 업로드·질문 요청을 관리하고, Zustand로 대화·출처·응답 ID를 메모리에 보관합니다. FastAPI 백엔드는 PDF를 파싱하고 청크로 나눈 뒤 OpenAI 임베딩을 생성합니다. 원본 PDF는 Supabase Storage, 메타데이터와 1536차원 벡터는 PostgreSQL/pgvector에 저장합니다.

Supabase SQL 편집기에서 위 마이그레이션을 직접 실행한 후, 백엔드 `.env`에 OpenAI 키·모델과 Supabase URL·서버 전용 키를 설정하세요. 프론트엔드에는 API 주소만 설정합니다. 두 서버를 실행하고 텍스트 PDF 업로드 → 색인 완료 → 문서 관련 질문 → 답변 아래 출처 확인 순서로 테스트하세요. 같은 파일을 다시 업로드하면 기존 문서를 재사용합니다.

검색은 질문 임베딩과 청크 벡터의 코사인 유사도로 상위 5개를 선택합니다. 모델은 현재 검색된 청크만 사실 근거로 사용하도록 지시받습니다. 관련 자료가 없으면 정보 부족을 반환합니다. 오래된 임베딩 없는 문서는 다시 업로드해야 하며, 대화 기록은 새로고침하면 사라집니다. 인증·에이전트·스트리밍·대화 DB는 범위에 포함하지 않았습니다. 로컬 자동 테스트는 외부 서비스를 대체하므로 실제 Supabase SQL 및 OpenAI 연동은 위 수동 테스트로 확인해야 합니다.
