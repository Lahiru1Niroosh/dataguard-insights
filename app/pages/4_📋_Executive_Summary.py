import streamlit as st
from app.queries.executive_summary import generate_summary_text, get_latest_run_summary
from app.theme import inject_base_styles, ledger_row, status_pill

st.set_page_config(layout="wide")
inject_base_styles()
st.title("Executive Summary")
st.markdown('<div class="hero-accent"></div>', unsafe_allow_html=True)

data = get_latest_run_summary()

if not data:
    st.warning("No run data available yet.")
else:
    is_healthy = data["integrity_pct"] is not None and data["integrity_pct"] >= 99.5

    with st.container(border=True):
        st.markdown(
            f'### {generate_summary_text()} {status_pill(is_healthy)}',
            unsafe_allow_html=True,
        )

        ledger_row([
            {"label": "Discrepancies", "value": str(data["discrepancy_count"]), "accent": "red"},
            {"label": "Dollar Impact", "value": f"${data['dollar_impact']:,.2f}", "accent": "gold"},
            {"label": "Accounts Affected", "value": str(data["affected_accounts"])},
            {"label": "Integrity %", "value": f"{data['integrity_pct']}%" if data["integrity_pct"] is not None else "N/A", "accent": "teal"},
        ])

    st.caption(
        "This summary is generated entirely from live data in dataguard_meta — "
        "re-run the Core pipeline with different fault injection and this text "
        "will update automatically to reflect it."
    )