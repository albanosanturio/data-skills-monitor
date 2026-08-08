-- ============================================================================
-- JOBS TABLE: Raw scraped job postings
-- ============================================================================
CREATE TABLE jobs (
  job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source VARCHAR(50),
  job_source_id VARCHAR(50),
  country VARCHAR(255),
  job_title VARCHAR(255),
  company_name VARCHAR(255),
  job_url VARCHAR(500),
  job_description TEXT,
  posted_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  skill_extraction_date TIMESTAMP DEFAULT NULL,
  CONSTRAINT source_and_id_unique UNIQUE (source, job_source_id)
);

CREATE INDEX idx_posted_date ON jobs (posted_date);

