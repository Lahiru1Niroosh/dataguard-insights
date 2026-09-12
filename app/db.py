"""
Phase B1 — Read-only data access layer.
Connects to dataguard_meta using a dedicated read-only Postgres role
(dataguard_readonly) — never dataguard-core's write credentials.
Uses SQLAlchemy's engine (not a raw psycopg2 connection) since
that's what pandas.read_sql_query expects natively.
"""
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "55432")
DB_NAME = os.getenv("DATABASE_NAME", "dataguard")
DB_USER = os.getenv("DATABASE_USER", "dataguard_readonly")
DB_PASS = os.getenv("DATABASE_PASSWORD", "dataguard_readonly_pw")

_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """
    Runs a SELECT query against dataguard_meta and returns a
    Pandas DataFrame. This is the single access point every
    query module in app/queries/ should go through.
    """
    return pd.read_sql_query(sql, _engine, params=params)