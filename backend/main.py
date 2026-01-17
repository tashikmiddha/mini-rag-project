from fastapi import FastAPI
from pydantic import BaseModel
from backend.rag import ingest, retrieve
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="Mini RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten in prod if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()


class Query(BaseModel):
    document: str
    question: str


@app.post("/query")
def query_rag(data: Query):
    """
    1. Ingest user document into vector DB
    2. Retrieve + rerank relevant chunks
    3. Generate grounded answer with citations
    """
    start = time.time()

    # 1️⃣ Ingest document
    ingest(data.document)

    # 2️⃣ Retrieve relevant context
    contexts = retrieve(data.question)

    if not contexts:
        return {
            "answer": "No relevant information found in the provided document.",
            "sources": [],
            "time": round(time.time() - start, 2)
        }

    # 3️⃣ Build citation-aware context
    context_text = ""
    for i, c in enumerate(contexts):
        context_text += f"[{i+1}] {c}\n\n"

    prompt = f"""
Answer the question using ONLY the context below.
Cite facts inline like [1], [2].

Context:
{context_text}

Question:
{data.question}
"""

    # 4️⃣ LLM answer
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer using provided context only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": contexts,
        "time": round(time.time() - start, 2)
    }
