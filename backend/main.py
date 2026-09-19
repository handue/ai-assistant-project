from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    # ex) GET, POST, PUT, DELETE, OPTIONS
    allow_headers = ["*"]
    # ex) Authorization, Set-Cookie, Cookie, Content-Type, Accept, X-Requested-With
)

# way to run : uvicorn main:app --reload

@app.get("/health")
def health():
    return {
        "status": "ok"
    }