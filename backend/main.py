from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

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
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


# way to run : python -m uvicorn main:app --reload
# 실행 방법: python -m uvicorn main:app --reload


@app.get("/health")
def health():

    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    return {"answer": f"You asked: {request.question}"}
