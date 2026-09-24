import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from uuid import uuid4

from supabase_client import supabase

load_dotenv()

app = FastAPI()

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    # ex) GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],
    # ex) Authorization, Set-Cookie, Cookie, Content-Type, Accept, X-Requested-With
)


# BaseModel: defines the request/response data shape.
# BaseModel: 요청/응답 데이터의 구조를 정의함.
# ex) AskReuqest(BaseModel) -> {"question": "What is AI?"} -> you can use it as 'request.question'
class AskRequest(BaseModel):
    question: str
    previous_response_id: str | None = None


class AskResponse(BaseModel):
    answer: str
    response_id: str


# way to run : python -m uvicorn main:app --reload
# 실행 방법: python -m uvicorn main:app --reload


@app.get("/health")
def health():

    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    response = client.responses.create(
        model=MODEL,
        input=request.question,
        previous_response_id=request.previous_response_id,
    )

    return {"answer": response.output_text, "response_id": response.id}


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    file_bytes = await file.read()
    document_id = str(uuid4())

    storage_path = f"{document_id}/{file.filename}"

    supabase.storage.from_("documents").upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": "application/pdf",
            "upsert": "false",
        },
    )

    document = (
        supabase.table("documents")
        .insert(
            {
                "id": document_id,
                "title": file.filename,
                "original_filename": file.filename,
                "storage_path": storage_path,
                "mime_type": file.content_type,
            }
        )
        .execute()
    )

    return {"document": document.data[0]}
