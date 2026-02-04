CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS project_chunks (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(255),
    content TEXT,
    embedding VECTOR(768)
);

CREATE INDEX ON project_chunks USING hnsw (embedding vector_cosine_ops);