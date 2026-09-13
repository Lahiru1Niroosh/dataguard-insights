"""
Phase B1 — Read-only data access layer.
Connects to dataguard_meta using a dedicated read-only Postgres role
— never dataguard-core's write credentials. Reads from Streamlit's
st.secrets when deployed (Streamlit Cloud), falling back to .env for
local development, so the same code runs in both places unchanged.
"""
import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def _get_setting(key: str, default: str = None) -> str:
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)


DB_HOST = _get_setting("DATABASE_HOST", "localhost")
DB_PORT = _get_setting("DATABASE_PORT", "55432")
DB_NAME = _get_setting("DATABASE_NAME", "dataguard")
DB_USER = _get_setting("DATABASE_USER", "dataguard_readonly")
DB_PASS = _get_setting("DATABASE_PASSWORD", "dataguard_readonly_pw")

_engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    if "neon.tech" in DB_HOST
    else f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """
    Runs a SELECT query against dataguard_meta and returns a
    Pandas DataFrame. This is the single access point every
    query module in app/queries/ should go through.
    """
    return pd.read_sql_query(sql, _engine, params=params)