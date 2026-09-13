import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import plotly.graph_objects as go
from app.queries.trends import get_run_history
from app.theme import inject_base_styles, ledger_row, plotly_theme, status_pill, TEAL, RED, GOLD

st.set_page_config(page_title="DataGuard Insights", page_icon="🏦", layout="wide")
inject_base_styles()

st.title("DataGuard Insights")
st.markdown('<div class="hero-accent"></div>', unsafe_allow_html=True)
st.markdown(
    "Business-facing analytics on the DataGuard Core reconciliation engine — "
    "translating row-level data discrepancies into dollar exposure, affected "
    "accounts, and integrity trends."
)

ledger_row([
    {"label": "What this reconciles", "value": "Core banking → reporting replica"},
    {"label": "Detection accuracy", "value": "100% precision / recall", "accent": "teal"},
    {"label": "Speedup vs naive SQL", "value": "2.3×–6.4×", "accent": "gold"},
])

st.markdown("&nbsp;")

df = get_run_history()

if df.empty:
    st.warning("No valid runs recorded yet.")
else:
    latest = df.iloc[-1]
    is_healthy = latest["integrity_pct"] >= 99.5

    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=latest["integrity_pct"],
                number={"suffix": "%", "font": {"size": 48, "color": GOLD}},
                title={"text": "Data Integrity — Latest Run", "font": {"size": 15}},
                gauge={
                    "axis": {"range": [95, 100], "tickwidth": 1},
                    "bar": {"color": TEAL},
                    "bgcolor": "#0B0F14",
                    "steps": [
                        {"range": [95, 98], "color": "#3A1E1E"},
                        {"range": [98, 99.5], "color": "#3A331A"},
                        {"range": [99.5, 100], "color": "#1B3A30"},
                    ],
                    "threshold": {"line": {"color": RED, "width": 3}, "thickness": 0.85, "value": 99.5},
                },
            ))
            gauge.update_layout(height=300, **plotly_theme())
            st.plotly_chart(gauge, use_container_width=True)
            st.markdown(
                f'Status: {status_pill(is_healthy)}',
                unsafe_allow_html=True,
            )
        with col2:
            ledger_row([
                {"label": "Discrepancies (latest run)", "value": f'{int(latest["discrepancy_count"])}'},
                {"label": "Dollar impact (latest run)", "value": f'${latest["dollar_impact"]:,.0f}', "accent": "red"},
                {"label": "Runs tracked", "value": f'{len(df)}'},
            ])

    st.markdown("&nbsp;")

    with st.container(border=True):
        st.markdown("##### Run history")
        display_df = df[["run_seq", "started_at", "total_rows_checked", "discrepancy_count", "dollar_impact", "integrity_pct"]]
        display_df = display_df.rename(columns={"run_seq": "run"})
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "dollar_impact": st.column_config.NumberColumn("dollar_impact", format="$%,.2f"),
                "integrity_pct": st.column_config.ProgressColumn(
                    "integrity_pct", min_value=95, max_value=100, format="%.2f%%"
                ),
            },
        )