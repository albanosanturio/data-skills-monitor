import sqlalchemy
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres.nqttybtwpuylpuwontww:queti4041111@aws-1-us-west-2.pooler.supabase.com:5432/postgres"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())