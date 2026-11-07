CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS app_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(150) NOT NULL, password_hash TEXT NOT NULL, role VARCHAR(20) NOT NULL CHECK(role IN ('ADMIN','USER')),
  is_active BOOLEAN NOT NULL DEFAULT TRUE, token_limit_monthly INTEGER NOT NULL DEFAULT 20000,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS ai_services (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), code VARCHAR(40) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, description TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS catalog_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), title VARCHAR(255) NOT NULL, category VARCHAR(20) NOT NULL CHECK(category IN ('MOVIE','GAME')),
  synopsis TEXT NOT NULL, genre VARCHAR(120), platform VARCHAR(120), release_year INTEGER,
  rating NUMERIC(3,1), duration_minutes INTEGER, players VARCHAR(50), is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS catalog_search_idx ON catalog_items USING GIN (to_tsvector('spanish', title || ' ' || synopsis || ' ' || coalesce(genre,'')));
CREATE INDEX IF NOT EXISTS catalog_title_trgm_idx ON catalog_items USING GIN (title gin_trgm_ops);
CREATE TABLE IF NOT EXISTS conversations (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id UUID REFERENCES app_users(id), service_code VARCHAR(40) NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS chat_messages (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE, role VARCHAR(20) NOT NULL, content TEXT NOT NULL, sources JSONB NOT NULL DEFAULT '[]', created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS usage_logs (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id UUID REFERENCES app_users(id), service_code VARCHAR(40) NOT NULL, request_tokens INTEGER NOT NULL DEFAULT 0, response_tokens INTEGER NOT NULL DEFAULT 0, total_tokens INTEGER NOT NULL DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS api_keys (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name VARCHAR(100) NOT NULL, key_hash TEXT NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE OR REPLACE VIEW vw_consumption_report AS SELECT date(created_at) AS date, service_code AS service, count(*) AS requests, sum(request_tokens) AS input_tokens, sum(response_tokens) AS output_tokens, sum(total_tokens) AS total_tokens FROM usage_logs GROUP BY date(created_at), service_code;
INSERT INTO ai_services(code,name,description) VALUES ('rag','Chat RAG','Consultas basadas en el catálogo'),('recommend','Recomendador','Recomendaciones con fuentes externas'),('news','Novedades','Novedades y sagas') ON CONFLICT (code) DO NOTHING;
