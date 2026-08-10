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


-- ============================================================================
-- JSKILLS TABLE SEED: Data engineering / analytics skills for regex
-- ============================================================================


INSERT INTO skills (skill_name, category, tags) VALUES

-- CORE LANGUAGES
('Python', 'language', ARRAY['general-purpose', 'scripting']),
('SQL', 'language', ARRAY['query-language', 'standard']),
('Scala', 'language', ARRAY['big-data', 'functional']),
('Java', 'language', ARRAY['big-data', 'general-purpose']),
('Golang', 'language', ARRAY['infrastructure', 'performance']),
('Bash', 'language', ARRAY['scripting', 'automation']),

-- BIG DATA & COMPUTE
('Spark', 'platform', ARRAY['big-data', 'distributed-computing']),
('PySpark', 'platform', ARRAY['python', 'big-data']),
('Hadoop', 'platform', ARRAY['big-data', 'distributed-computing']),
('Hive', 'platform', ARRAY['sql-on-hadoop', 'big-data']),
('Presto', 'platform', ARRAY['sql-engine', 'distributed-query']),
('Trino', 'platform', ARRAY['sql-engine', 'distributed-query']),
('Flink', 'platform', ARRAY['streaming', 'real-time']),

-- DATA WAREHOUSING
('Snowflake', 'platform', ARRAY['cloud-native', 'data-warehouse']),
('BigQuery', 'platform', ARRAY['cloud-native', 'data-warehouse']),
('Redshift', 'platform', ARRAY['aws', 'data-warehouse']),
('Azure Synapse', 'platform', ARRAY['azure', 'data-warehouse']),
('Databricks', 'platform', ARRAY['lakehouse', 'ai-ml']),
('PostgreSQL', 'platform', ARRAY['relational', 'open-source']),
('DuckDB', 'platform', ARRAY['olap', 'embedded']),

-- ORCHESTRATION & ELT
('dbt', 'orchestration', ARRAY['elt', 'testing', 'data-modeling', 'data-quality']),
('Airflow', 'orchestration', ARRAY['workflow-scheduling', 'orchestration']),
('Prefect', 'orchestration', ARRAY['workflow-scheduling', 'orchestration']),
('Dagster', 'orchestration', ARRAY['workflow-scheduling', 'data-aware']),
('Fivetran', 'orchestration', ARRAY['elt', 'managed-service']),
('Airbyte', 'orchestration', ARRAY['elt', 'open-source']),
('Azure Data Factory', 'orchestration', ARRAY['azure', 'elt', 'managed-service']),

-- DATA LAKES & FORMATS
('Delta Lake', 'storage', ARRAY['lakehouse', 'acid-transactions']),
('Iceberg', 'storage', ARRAY['lakehouse', 'schema-evolution']),
('Hudi', 'storage', ARRAY['lakehouse', 'incremental-processing']),
('Apache Avro', 'storage', ARRAY['serialization', 'schema-evolution']),
('Parquet', 'storage', ARRAY['columnar', 'compression']),

-- STREAMING & MESSAGING
('Kafka', 'streaming', ARRAY['event-streaming', 'messaging']),
('RabbitMQ', 'streaming', ARRAY['messaging', 'reliability']),
('Pub/Sub', 'streaming', ARRAY['google-cloud', 'managed-service']),

-- CLOUD PLATFORMS
('AWS', 'cloud', ARRAY['cloud-platform']),
('Amazon Web Services', 'cloud', ARRAY['cloud-platform']),
('GCP', 'cloud', ARRAY['cloud-platform']),
('Google Cloud Platform', 'cloud', ARRAY['cloud-platform']),
('Azure', 'cloud', ARRAY['cloud-platform']),

-- CLOUD STORAGE
('S3', 'storage', ARRAY['aws', 'object-storage']),
('GCS', 'storage', ARRAY['google-cloud', 'object-storage']),
('Azure Data Lake', 'storage', ARRAY['azure', 'data-lake']),

-- DATABASES
('MySQL', 'database', ARRAY['relational', 'open-source']),
('MongoDB', 'database', ARRAY['nosql', 'document-database']),
('Cassandra', 'database', ARRAY['nosql', 'distributed']),
('Elasticsearch', 'database', ARRAY['search', 'analytics']),
('Redis', 'database', ARRAY['nosql', 'in-memory', 'caching']),
('DynamoDB', 'database', ARRAY['nosql', 'aws']),
('SQL Server', 'database', ARRAY['relational', 'microsoft']),

-- BUSINESS INTELLIGENCE
('Tableau', 'bi', ARRAY['visualization', 'enterprise']),
('Power BI', 'bi', ARRAY['visualization', 'microsoft']),
('PowerBI', 'bi', ARRAY['visualization', 'microsoft']),
('Looker', 'bi', ARRAY['visualization', 'business-intelligence']),
('Metabase', 'bi', ARRAY['visualization', 'open-source']),
('Superset', 'bi', ARRAY['visualization', 'open-source']),

-- TESTING & DATA QUALITY
('Great Expectations', 'tool', ARRAY['testing', 'data-quality', 'validation']),
('Monte Carlo', 'tool', ARRAY['monitoring', 'data-quality']),

-- DEVOPS & INFRASTRUCTURE
('Docker', 'devops', ARRAY['containerization', 'infrastructure']),
('Kubernetes', 'devops', ARRAY['container-orchestration', 'infrastructure']),
('Terraform', 'devops', ARRAY['infrastructure-as-code', 'automation']),
('Jenkins', 'devops', ARRAY['ci-cd', 'automation']),
('GitHub Actions', 'devops', ARRAY['ci-cd', 'automation']),
('GitLab CI', 'devops', ARRAY['ci-cd', 'automation']),
('GitLabCI', 'devops', ARRAY['ci-cd', 'automation']),
('CircleCI', 'devops', ARRAY['ci-cd', 'automation']),
('CI/CD', 'devops', ARRAY['automation', 'deployment']),


-- MACHINE LEARNING & DATA SCIENCE
('Scikit-learn', 'ml', ARRAY['machine-learning', 'python']),
('TensorFlow', 'ml', ARRAY['deep-learning', 'machine-learning']),
('PyTorch', 'ml', ARRAY['deep-learning', 'machine-learning']),
('XGBoost', 'ml', ARRAY['machine-learning', 'gradient-boosting']),
('LightGBM', 'ml', ARRAY['machine-learning', 'gradient-boosting']),
('MLOps', 'ml', ARRAY['machine-learning', 'infrastructure']),
('MLflow', 'ml', ARRAY['machine-learning', 'experiment-tracking']),
('Kubeflow', 'ml', ARRAY['machine-learning', 'orchestration']),

-- PYTHON LIBRARIES
('Pandas', 'tool', ARRAY['data-analysis', 'python']),
('NumPy', 'tool', ARRAY['numerical-computing', 'python']),
('Matplotlib', 'tool', ARRAY['visualization', 'python']),
('Plotly', 'tool', ARRAY['visualization', 'interactive']),

-- API & DATA FORMATS
('REST', 'tool', ARRAY['api-design', 'standard']),
('GraphQL', 'tool', ARRAY['api-design', 'modern']),
('Protocol Buffers', 'tool', ARRAY['serialization', 'google']),

-- MODERN DATA STACK & ARCHITECTURE
('Lakehouse', 'platform', ARRAY['architecture-pattern']),
('Data Mesh', 'platform', ARRAY['architecture-pattern']),

-- SQL ENGINES & QUERY LAYERS
('Athena', 'platform', ARRAY['aws', 'serverless', 'sql-engine']),
('Spark SQL', 'platform', ARRAY['sql-engine', 'distributed']),

-- AWS SERVICES
('SageMaker', 'platform', ARRAY['aws', 'machine-learning']),
('AWS Glue', 'orchestration', ARRAY['aws', 'elt', 'managed-service']),
('StepFunctions', 'orchestration', ARRAY['aws', 'workflow-orchestration']),

-- GOOGLE CLOUD SERVICES
('Vertex', 'platform', ARRAY['google-cloud', 'machine-learning']),
('Dataflow', 'platform', ARRAY['google-cloud', 'streaming', 'batch']),

-- LEGACY TOOLS (still appearing in job postings)
('Talend', 'orchestration', ARRAY['legacy', 'elt']),
('Informatica', 'orchestration', ARRAY['legacy', 'elt']),
('Oracle', 'database', ARRAY['legacy', 'relational']),
('Teradata', 'platform', ARRAY['legacy', 'data-warehouse'])

ON CONFLICT (skill_name) DO UPDATE SET
  category = EXCLUDED.category,
  tags = EXCLUDED.tags,
  created_at = CURRENT_TIMESTAMP;