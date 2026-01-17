import uuid
import os
from openai import OpenAI
import cohere

USE_MOCK = (
    os.getenv("OPENAI_API_KEY", "").startswith("your_") or 
    not os.getenv("OPENAI_API_KEY") or
    os.getenv("SUPABASE_URL", "").startswith("your_") or 
    not os.getenv("SUPABASE_URL")
)

if not USE_MOCK:
    client = OpenAI()
    co = cohere.Client()

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 120

mock_chunks = []

def chunk_text(text):
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start = end - CHUNK_OVERLAP
    return chunks


def embed(text):
    return client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding


def ingest(text):
    global mock_chunks
    if USE_MOCK:
        mock_chunks = chunk_text(text)
        return
    
    from db import supabase
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

#retrieve the data from the supabase 
def retrieve(query):
    if USE_MOCK:
        global mock_chunks
        if not mock_chunks:
            return []
        query_words = query.lower().split()
        matched = [c for c in mock_chunks if any(word in c.lower() for word in query_words)]
        return matched[:4] if matched else mock_chunks[:1]
    
    from db import supabase
    q_embedding = embed(query)

    res = supabase.rpc("match_documents", {
        "query_embedding": q_embedding,
        "match_count": 8
    }).execute()

    docs = [r["content"] for r in res.data]
    
    if not docs:
        return []

    reranked = co.rerank(
        query=query,
        documents=docs,
        top_n=4
    )

    return [docs[r.index] for r in reranked.results]

