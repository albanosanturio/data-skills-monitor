-- data-skills-monitor: PostgreSQL Schema
-- Tables for storing job postings, skills, packages, and their relationships

-- ============================================================================
-- JOBS TABLE: Raw scraped job postings
-- ============================================================================
CREATE TABLE jobs (
  job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source VARCHAR(50) NOT NULL,  -- 'indeed', 'stackoverflow'
  job_title VARCHAR(255) NOT NULL,
  company_name VARCHAR(255),
  location VARCHAR(255),
  job_description TEXT NOT NULL,
  posted_date DATE,
  job_url VARCHAR(500),
  job_type VARCHAR(50),  -- 'remote', 'hybrid', 'onsite'
  scraped_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source_date ON jobs (source, scraped_date);
CREATE INDEX idx_posted_date ON jobs (posted_date);
CREATE INDEX idx_location ON jobs (location);

-- ============================================================================
-- SKILLS TABLE: Normalized skill catalog (predefined, regex-matched)
-- ============================================================================
CREATE TABLE skills (
  skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_name VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50),  -- 'language', 'platform', 'orchestration', 'cloud', 'storage', 'tool', 'bi'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_category ON skills (category);

-- ============================================================================
-- JOB_SKILLS TABLE: Many-to-many relationship between jobs and skills
-- ============================================================================
CREATE TABLE job_skills (
  job_skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
  extraction_method VARCHAR(50),  -- 'regex' (for MVP; will add 'claude' in future)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(job_id, skill_id)
);

CREATE INDEX idx_job_id ON job_skills (job_id);
CREATE INDEX idx_skill_id ON job_skills (skill_id);

-- ============================================================================
-- PACKAGES TABLE: Python packages tracked from PyPI
-- ============================================================================
CREATE TABLE packages (
  package_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  package_name VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50),  -- 'orchestration', 'platform', 'data_quality', 'language', etc.
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_packages_category ON packages (category);

-- ============================================================================
-- PACKAGE_DOWNLOADS TABLE: Time-series of PyPI download stats
-- ============================================================================
CREATE TABLE package_downloads (
  download_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  package_id UUID NOT NULL REFERENCES packages(package_id) ON DELETE CASCADE,
  date DATE NOT NULL,
  downloads INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(package_id, date)
);

CREATE INDEX idx_package_date ON package_downloads (package_id, date);
CREATE INDEX idx_date ON package_downloads (date);