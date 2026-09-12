"""
Phase B1 — Read-only data access layer.
Connects to dataguard_meta using a dedicated read-only Postgres role
(dataguard_readonly) — never dataguard-core's write credentials.
This is a deliberate least-privilege security decision: Insights
cannot modify Core's data even if there's a bug in this codebase.
"""
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "55432")
DB_NAME = os.getenv("DATABASE_NAME", "dataguard")
DB_USER = os.getenv("DATABASE_USER", "dataguard_readonly")
DB_PASS = os.getenv("DATABASE_PASSWORD", "dataguard_readonly_pw")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )


def run_query(sql: str, params: tuple = None) -> pd.DataFrame:
    """
    Runs a SELECT query against dataguard_meta and returns a
    Pandas DataFrame. This is the single access point every
    query module in app/queries/ should go through.
    """
    conn = get_conn()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()
    return df