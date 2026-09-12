import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(page_title="DataGuard Insights", layout="wide")

st.title("DataGuard Insights")
st.markdown("""
Business-facing analytics on top of the DataGuard Core reconciliation engine.
Use the sidebar to navigate between Overview, Trends, the Discrepancy Explorer,
and the Executive Summary.
""")