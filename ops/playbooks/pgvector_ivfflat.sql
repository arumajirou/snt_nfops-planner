-- ops/playbooks/pgvector_ivfflat.sql
-- 前提: CREATE EXTENSION IF NOT EXISTS vector;
-- 例: CREATE TABLE IF NOT EXISTS phase14_index (id SERIAL PRIMARY KEY, text TEXT, vec vector(384));
CREATE INDEX IF NOT EXISTS phase14_index_vec_ivfflat
ON phase14_index USING ivfflat (vec vector_cosine_ops) WITH (lists=100);
ANALYZE phase14_index;
