from fastapi import FastAPI
from pydantic import BaseModel
from rag import ingest, retrieve
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import time
import os

USE_MOCK = os.getenv("OPENAI_API_KEY", "").startswith("your_") or not os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    document: str
    question: str

@app.post("/query")
def query_rag(data: Query):
    start = time.time()

    ingest(data.document)
    contexts = retrieve(data.question)

    if not contexts:
        return {"answer": "No relevant info found.", "sources": []}

    context_text = ""
    for i, c in enumerate(contexts):
        context_text += f"[{i+1}] {c}\n"

    prompt = f"""
Answer using ONLY the context.
Cite facts like [1], [2].

Context:
{context_text}

Question:
{data.question}
"""
    
    if USE_MOCK:
        return {
            "answer": f"Based on the document: {contexts[0][:200]}...",
            "sources": contexts,
            "time": round(time.time() - start, 2)
        }

    client = OpenAI()
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer using provided context only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return {
        "answer": res.choices[0].message.content,
        "sources": contexts,
        "time": round(time.time() - start, 2)
    }

