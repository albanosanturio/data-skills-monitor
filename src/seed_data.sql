-- data-skills-monitor: Initial Seed Data
-- Skills catalog and packages to track
-- Run AFTER schema.sql

-- ============================================================================
-- INITIAL SKILLS (30 predefined skills for regex matching)
-- ============================================================================
INSERT INTO skills (skill_name, category) VALUES
-- Languages
('Python', 'language'),
('Scala', 'language'),
('Java', 'language'),
('SQL', 'language'),
('R', 'language'),
('Go', 'language'),

-- Platforms
('Apache Spark', 'platform'),
('BigQuery', 'platform'),
('Snowflake', 'platform'),
('Redshift', 'platform'),
('Databricks', 'platform'),
('Azure Synapse', 'platform'),
('DuckDB', 'platform'),

-- Orchestration
('Apache Airflow', 'orchestration'),
('dbt', 'orchestration'),
('Prefect', 'orchestration'),
('Dagster', 'orchestration'),

-- Cloud
('AWS', 'cloud'),
('GCP', 'cloud'),
('Azure', 'cloud'),

-- Storage
('S3', 'storage'),
('Delta Lake', 'storage'),
('Iceberg', 'storage'),
('PostgreSQL', 'storage'),

-- Tools
('Docker', 'tool'),
('Kubernetes', 'tool'),
('Git', 'tool'),
('Great Expectations', 'tool'),
('Apache Kafka', 'tool'),

-- BI
('Tableau', 'bi'),
('Power BI', 'bi'),
('Looker', 'bi');

-- ============================================================================
-- INITIAL PACKAGES (key Python packages to track)
-- ============================================================================
INSERT INTO packages (package_name, category) VALUES
-- Orchestration
('apache-airflow', 'orchestration'),
('dbt-core', 'orchestration'),
('prefect', 'orchestration'),
('dagster', 'orchestration'),

-- Platforms
('pyspark', 'platform'),
('databricks', 'platform'),

-- Data Processing
('pandas', 'data_processing'),
('polars', 'data_processing'),
('duckdb', 'data_processing'),

-- Data Quality
('great-expectations', 'data_quality'),
('soda-core', 'data_quality'),

-- Utilities
('sqlalchemy', 'utility'),
('requests', 'utility'),
('python-dotenv', 'utility'),
('pytest', 'testing');