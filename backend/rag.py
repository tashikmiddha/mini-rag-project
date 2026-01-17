import uuid
from openai import OpenAI
import cohere
from backend.db import supabase

# Clients
openai_client = OpenAI()
co = cohere.Client()

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 120


def chunk_text(text: str):
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start = end - CHUNK_OVERLAP
    return chunks


def embed(text: str):
    return openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding


def ingest(text: str):
    if not text.strip():
        return

    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        supabase.table("documents").insert({
            "id": str(uuid.uuid4()),
            "content": chunk,
            "embedding": embed(chunk),
            "source": "user_upload",
            "title": "Uploaded Text",
            "section": "N/A",
            "position": i
        }).execute()


def retrieve(query: str):
    q_embedding = embed(query)

    res = supabase.rpc(
        "match_documents",
        {
            "query_embedding": q_embedding,
            "match_count": 8
        }
    ).execute()

    if not res.data:
        return []

    docs = [row["content"] for row in res.data]

    reranked = co.rerank(
        query=query,
        documents=docs,
        top_n=4
    )

    return [docs[r.index] for r in reranked.results]
