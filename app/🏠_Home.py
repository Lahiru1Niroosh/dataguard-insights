import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import plotly.graph_objects as go
from app.queries.trends import get_run_history
from app.theme import (
    inject_base_styles, ledger_row, plotly_theme, status_pill,
    hero, section_header, TEAL, RED, GOLD,
)

st.set_page_config(page_title="DataGuard Insights", page_icon="🏦", layout="wide")
inject_base_styles()

# ---------------- Hero ----------------
hero(
    eyebrow="DataGuard Core · Reconciliation",
    title="DataGuard Insights",
    lede=(
        "Business-facing analytics on the DataGuard Core reconciliation engine — "
        "translating row-level data discrepancies into dollar exposure, affected "
        "accounts, and integrity trends."
    ),
    meta_html=(
        "<div>Last refreshed</div>"
        "<div><strong>just now</strong></div>"
        "<div style='margin-top:0.6rem;'>Source</div>"
        "<div><strong>core_banking → reporting_replica</strong></div>"
    ),
)

# ---------------- Top ledger ----------------
section_header("At a glance", "engine capability")
ledger_row([
    {"label": "What this reconciles", "value": "Core banking → reporting replica"},
    {"label": "Detection accuracy",   "value": "100% precision / recall", "accent": "teal"},
    {"label": "Speedup vs naive SQL", "value": "2.3×–6.4×",               "accent": "gold"},
])

# ---------------- Data ----------------
df = get_run_history()

if df.empty:
    st.markdown(
        '<div style="border:1px dashed #2A3340;border-radius:14px;'
        'padding:3rem;text-align:center;color:#8B96A5;font-size:0.95rem;">'
        'No valid runs recorded yet.'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    latest = df.iloc[-1]
    is_healthy = latest["integrity_pct"] >= 99.5

    # ---------------- Latest run: gauge + ledger ----------------
    section_header("Latest run", f"run #{int(latest['run_seq'])}")

    # Hero gauge — full width, big, unmistakable
    with st.container(border=True):
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest["integrity_pct"],
            number={
                "suffix": "%",
                "font": {"size": 68, "color": GOLD,
                         "family": "Source Serif 4, serif"},
            },
            title={"text": "Data Integrity", "font": {"size": 14, "color": "#8B96A5"}},
            gauge={
                "axis": {"range": [95, 100], "tickwidth": 1},
                "bar": {"color": TEAL, "thickness": 0.30},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [95, 98],    "color": "rgba(214,69,69,0.18)"},
                    {"range": [98, 99.5],  "color": "rgba(201,162,39,0.18)"},
                    {"range": [99.5, 100], "color": "rgba(63,167,150,0.18)"},
                ],
                "threshold": {
                    "line": {"color": RED, "width": 3},
                    "thickness": 0.85,
                    "value": 99.5,
                },
            },
        ))
        gauge.update_layout(
            height=320,
            **{**plotly_theme(), "margin": dict(t=30, b=10, l=40, r=40)},
        )
        st.plotly_chart(gauge, use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown(
            f'<div style="text-align:center;margin-top:-0.35rem;">'
            f'{status_pill(is_healthy)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("&nbsp;")

    # Ledger strip directly under the gauge — full width, no more empty band
    ledger_row([
        {"label": "Discrepancies",
         "value": f'{int(latest["discrepancy_count"]):,}'},
        {"label": "Dollar impact",
         "value": f'${latest["dollar_impact"]:,.0f}', "accent": "red"},
        {"label": "Rows checked",
         "value": f'{int(latest["total_rows_checked"]):,}'},
        {"label": "Integrity",
         "value": f'{latest["integrity_pct"]:.2f}%', "accent": "teal"},
    ])

    st.markdown("&nbsp;")

    # ---------------- Run history ----------------
    section_header("Run history", f"{len(df)} validated passes")

    with st.container(border=True):
        display_df = df[[
            "run_seq", "started_at", "total_rows_checked",
            "discrepancy_count", "dollar_impact", "integrity_pct",
        ]].rename(columns={
            "run_seq": "Run",
            "started_at": "Started",
            "total_rows_checked": "Rows checked",
            "discrepancy_count": "Discrepancies",
            "dollar_impact": "Dollar impact",
            "integrity_pct": "Integrity",
        })

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Dollar impact": st.column_config.NumberColumn(
                    "Dollar impact", format="$%,.2f"
                ),
                "Integrity": st.column_config.ProgressColumn(
                    "Integrity", min_value=95, max_value=100, format="%.2f%%"
                ),
                "Rows checked": st.column_config.NumberColumn(
                    "Rows checked", format="%,d"
                ),
            },
        )