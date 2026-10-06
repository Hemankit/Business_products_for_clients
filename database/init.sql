CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,

    client_id TEXT NOT NULL,

    document_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    source TEXT,

    chunk_index INTEGER NOT NULL,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    embedding VECTOR(1024) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (client_id, document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_client_id
    ON knowledge_chunks (client_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document_id
    ON knowledge_chunks (document_id);