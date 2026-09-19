from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin = {"http://localhost:3000"},
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

#uvicorn main:app --reload

@app.get("/health")
def health():
    return {
        "status": "ok"
    }