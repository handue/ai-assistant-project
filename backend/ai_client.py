import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).with_name(".env"))

client = OpenAI(timeout=60.0, max_retries=2)
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = 1536


def create_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for start in range(0, len(texts), 64):
        batch = texts[start : start + 64]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL, input=batch, dimensions=EMBEDDING_DIMENSIONS,
        )
        vectors = [item.embedding for item in sorted(response.data, key=lambda item: item.index)]
        if len(vectors) != len(batch) or any(len(vector) != EMBEDDING_DIMENSIONS for vector in vectors):
            raise RuntimeError("Unexpected embedding dimensions or count.")
        embeddings.extend(vectors)
    return embeddings
