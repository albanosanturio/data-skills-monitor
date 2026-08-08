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


-- ============================================================================
-- SKILLS TABLE: Normalized skill catalog (predefined, regex-matched)
-- ============================================================================
CREATE TABLE skills (
  skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_name VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50),  -- 'language', 'platform', 'orchestration', 'cloud', 'storage', 'tool', 'bi'
  tags TEXT[] DEFAULT '{}'::TEXT[],
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- JOB_SKILLS TABLE: Many-to-many relationship between jobs and skills
-- ============================================================================
CREATE TABLE job_skills (
  job_skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
  job_title VARCHAR(255),
  skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
  skill_name VARCHAR(100),
  extraction_method VARCHAR(50),  -- 'regex' (for MVP; will add 'claude' in future)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(job_id, skill_id)
);

CREATE INDEX idx_job_id ON job_skills (job_id);
CREATE INDEX idx_skill_id ON job_skills (skill_id);