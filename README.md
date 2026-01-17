# Mini RAG - AI Engineer Assessment (Track B)

A Retrieval-Augmented Generation (RAG) application that lets users input text, stores it in a cloud vector database, retrieves relevant chunks, reranks them, and generates grounded answers with citations.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React + Vite)                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Text Input  │    │  Query Box   │    │  Answer Panel    │  │
│  └──────────────┘    └──────────────┘    │  + Citations     │  │
│                                           └──────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP POST /query
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│  ┌────────────────┐    ┌────────────────┐    ┌──────────────┐  │
│  │   Ingest       │───▶│   Retrieve     │───▶│   LLM        │  │
│  │ (chunk + embed)│    │ (top-k + rerank)│    │ (GPT-4o-mini)│  │
│  └────────────────┘    └────────────────┘    └──────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Supabase (pgvector)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  documents: id, content, embedding(1536), metadata       │  │
│  │  match_documents: RPC function for cosine similarity     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

### Vector Database
- **Provider**: Supabase pgvector
- **Table**: `documents`
- **Embedding Dimension**: 1536 (OpenAI text-embedding-3-small)
- **Distance Metric**: Cosine Similarity
- **Upsert Strategy**: Insert on ingest (no updates)

### Chunking Strategy
- **Chunk Size**: 1000 characters
- **Overlap**: 120 characters (~12%)
- **Metadata Stored**: source, title, section, position

### Retriever + Reranker
- **Top-k**: 8 documents retrieved
- **Reranker**: Cohere Rerank v3.5
- **Final Top-n**: 4 documents after reranking

### LLM Provider
- **Model**: GPT-4o-mini (OpenAI)
- **Temperature**: 0 (deterministic)
- **System Prompt**: "Answer using provided context only"

## Requirements Met

| Requirement | Status | Details |
|------------|--------|---------|
| Cloud Vector DB | ✅ | Supabase pgvector |
| Embeddings | ✅ | OpenAI text-embedding-3-small |
| Chunking | ✅ | 1000 chars, 120 overlap |
| Metadata | ✅ | source, title, section, position |
| Top-k Retrieval | ✅ | 8 docs via cosine similarity |
| Reranker | ✅ | Cohere Rerank |
| LLM | ✅ | GPT-4o-mini |
| Citations | ✅ | [1], [2] format |
| Frontend | ✅ | React + Vite |
| Timing | ✅ | Request time displayed |
| Server-side Keys | ✅ | All keys in .env |

## Setup

### 1. Clone and Install
```bash
git clone https://github.com/tashikmiddha/mini-rag-project.git
cd intern project
pip install -r backend/requirement.txt
cd frontend && npm install
```

### 2. Configure Environment
Copy `backend/.env.example` to `backend/.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. Set Up Supabase
Run `backend/supabase_setup.sql` in your Supabase SQL Editor.

### 4. Run Locally
```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 5. Deploy
See [DEPLOY.md](DEPLOY.md) for Vercel + Render deployment guide.

## Gold Set Q/A Pairs

Test the app with this document and questions:

**Document:**
```
Artificial Intelligence (AI) refers to the simulation of human intelligence in machines programmed 
to think and learn like humans. The term may also be applied to any machine that exhibits traits 
associated with a human mind, such as learning and problem-solving.

Machine learning is a subset of AI that enables systems to learn and improve from experience 
automatically without being explicitly programmed. It focuses on developing computer programs 
that can access data and use it to learn for themselves.

Deep learning is a subset of machine learning that uses artificial neural networks with multiple 
layers to progressively extract higher-level features from raw input. It has revolutionized 
computer vision, speech recognition, and natural language processing.
```

**Q/A Pairs:**

| # | Question | Expected Answer |
|---|----------|-----------------|
| 1 | What is AI? | Simulation of human intelligence in machines |
| 2 | What is machine learning? | Subset of AI that enables systems to learn from experience |
| 3 | What is deep learning? | Subset using neural networks with multiple layers |
| 4 | What has deep learning revolutionized? | Computer vision, speech recognition, NLP |
| 5 | How does machine learning improve? | By accessing and learning from data automatically |

## Performance Notes

- **Precision**: High when query keywords match document content
- **Recall**: Depends on embedding similarity threshold
- **Latency**: 0.5-2s typical (dominated by OpenAI API calls)

## Remarks

### Trade-offs Made
1. **Mock Mode**: Added fallback when API keys are missing for testing
2. **Simple Chunking**: Character-based (not token-based) for simplicity
3. **No Updates**: Only insert, no update/delete functionality

### Provider Limits
- OpenAI: Rate limits may apply on free tier
- Cohere: 10 trial API calls/day on free tier
- Supabase: Free tier has database size limits

### Future Improvements
- Add document upload (PDF/TXT parsing)
- Implement MMR for diverse retrieval
- Add streaming responses
- Support multiple collections
- Add user authentication

