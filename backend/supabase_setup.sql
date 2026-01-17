CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(1536),
    source TEXT,
    title TEXT,
    section TEXT,
    position INTEGER
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_count INTEGER DEFAULT 8
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

