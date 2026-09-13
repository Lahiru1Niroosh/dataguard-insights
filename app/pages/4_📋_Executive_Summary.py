import streamlit as st
from app.queries.executive_summary import generate_summary_text, get_latest_run_summary
from app.theme import (
    inject_base_styles, ledger_row, status_pill,
    hero, section_header,
    RED, GOLD, TEAL, MUTED_TEXT, BORDER, TEXT,
)

st.set_page_config(layout="wide")
inject_base_styles()

# ---------------- Hero ----------------
hero(
    eyebrow="DataGuard Core · Executive Summary",
    title="Executive Summary",
    lede=(
        "A one-page narrative of the latest reconciliation run — what was "
        "checked, what didn't reconcile, and what it's worth. Generated "
        "directly from live data; nothing here is hand-written."
    ),
    meta_html=(
        "<div>Basis</div>"
        "<div><strong>latest recorded run</strong></div>"
        "<div style='margin-top:0.5rem;'>Source</div>"
        "<div><strong>dataguard_meta</strong></div>"
    ),
)

# ---------------- Data ----------------
data = get_latest_run_summary()

if not data:
    st.markdown(
        '<div style="border:1px dashed #2A3340;border-radius:14px;'
        'padding:2.5rem;text-align:center;color:#8B96A5;font-size:0.95rem;">'
        'No run data available yet.'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    is_healthy = data["integrity_pct"] is not None and data["integrity_pct"] >= 99.5

    # ============================================================
    # Narrative headline — styled as a pull-quote with gold rule
    # ============================================================
    section_header("Latest run narrative", "auto-generated")

    st.markdown(
        f'<div style="position:relative;'
        f'border:1px solid {BORDER};border-radius:14px;'
        f'background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0) 160px), #131A24;'
        f'padding:1.35rem 1.5rem 1.35rem 1.75rem;'
        f'box-shadow:0 1px 0 rgba(255,255,255,0.03) inset, 0 12px 32px -22px rgba(0,0,0,0.9);">'
        f'  <div style="position:absolute;left:0;top:1.35rem;bottom:1.35rem;'
        f'              width:3px;border-radius:2px;'
        f'              background:linear-gradient(180deg,{GOLD},{TEAL});"></div>'
        f'  <div style="font-family:\'Source Serif 4\',serif;'
        f'              font-size:1.32rem;line-height:1.5;font-weight:600;'
        f'              color:{TEXT};letter-spacing:-0.01em;">'
        f'    {generate_summary_text()}'
        f'    <span style="margin-left:0.5rem;vertical-align:middle;">'
        f'      {status_pill(is_healthy)}'
        f'    </span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ============================================================
    # Key figures — flush under the narrative, tighter card
    # ============================================================
    section_header("Key figures", "latest run")

    with st.container(border=True):
        ledger_row([
            {"label": "Discrepancies",
             "value": str(data["discrepancy_count"]),
             "accent": "red"},
            {"label": "Dollar impact",
             "value": f"${data['dollar_impact']:,.2f}",
             "accent": "gold"},
            {"label": "Accounts affected",
             "value": str(data["affected_accounts"])},
            {"label": "Integrity",
             "value": f"{data['integrity_pct']}%" if data["integrity_pct"] is not None else "N/A",
             "accent": "teal"},
        ])

    # ============================================================
    # Provenance note — inline, not pushed to the bottom
    # ============================================================
    st.markdown(
        '<div style="margin-top:0.75rem;border-left:2px solid #2A3340;'
        'padding:0.3rem 0 0.3rem 0.9rem;color:#8B96A5;font-size:0.82rem;'
        'line-height:1.5;max-width:80ch;">'
        'Generated from live data in '
        '<span style="color:#E8E6DE;font-weight:500;">dataguard_meta</span>. '
        'Re-run the Core pipeline with different fault injection and this text '
        'updates automatically.'
        '</div>',
        unsafe_allow_html=True,
    )