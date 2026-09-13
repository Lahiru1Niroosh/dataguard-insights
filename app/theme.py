"""
Shared visual identity for DataGuard Insights: an "audit ledger"
aesthetic, not a generic dark SaaS dashboard. One place to change
color/type for the whole app.
"""
import streamlit as st

INK = "#0B0F14"
PANEL = "#131A24"
BORDER = "#2A3340"
TEXT = "#E8E6DE"
MUTED_TEXT = "#8B96A5"
TEAL = "#3FA796"      # verified / passing state
RED = "#D64545"       # discrepancy / risk
GOLD = "#C9A227"      # one hero number per page, used sparingly


def inject_base_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3 {{
        font-family: 'Source Serif 4', serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }}
    [data-testid="stMetricValue"] {{
        font-variant-numeric: tabular-nums;
        font-weight: 700;
    }}
    [data-testid="stMetricLabel"] {{ color: {MUTED_TEXT}; font-size: 0.8rem; }}

    .ledger-row {{
        display: flex;
        border-top: 1px solid {BORDER};
        border-bottom: 1px solid {BORDER};
        padding: 1.25rem 0;
        margin: 1rem 0 1.5rem 0;
    }}
    .ledger-row > div {{
        flex: 1;
        padding: 0 1.5rem;
        border-right: 1px solid {BORDER};
    }}
    .ledger-row > div:first-child {{ padding-left: 0; }}
    .ledger-row > div:last-child {{ border-right: none; }}
    .ledger-label {{ color: {MUTED_TEXT}; font-size: 0.8rem; margin-bottom: 0.3rem; }}
    .ledger-value {{
        font-variant-numeric: tabular-nums;
        font-weight: 700;
        font-size: 1.9rem;
        color: {TEXT};
    }}
    .ledger-value.gold {{ color: {GOLD}; }}
    .ledger-value.red {{ color: {RED}; }}
    .ledger-value.teal {{ color: {TEAL}; }}
    .status-pill {{
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-left: 0.75rem;
        vertical-align: middle;
    }}
    .status-pill.ok {{
        background: rgba(63,167,150,0.15);
        color: {TEAL};
        border: 1px solid rgba(63,167,150,0.4);
    }}
    .status-pill.warn {{
        background: rgba(214,69,69,0.15);
        color: {RED};
        border: 1px solid rgba(214,69,69,0.4);
    }}
    .hero-accent {{
        height: 3px;
        width: 64px;
        background: linear-gradient(90deg, {GOLD}, {TEAL});
        border-radius: 2px;
        margin: 0.7rem 0 1.6rem 0;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {BORDER} !important;
        border-radius: 10px !important;
    }}
    .block-container {{
        padding-top: 2.5rem;
        max-width: 1400px;
    }}
    </style>
    """, unsafe_allow_html=True)


def status_pill(is_healthy: bool, ok_text: str = "Healthy", warn_text: str = "Needs attention") -> str:
    cls = "ok" if is_healthy else "warn"
    text = ok_text if is_healthy else warn_text
    return f'<span class="status-pill {cls}">{text}</span>'


def ledger_row(items: list[dict]):
    """items: [{'label': str, 'value': str, 'accent': 'gold'|'red'|'teal'|None}, ...]"""
    cells = "".join(
        f'<div><div class="ledger-label">{i["label"]}</div>'
        f'<div class="ledger-value {i.get("accent") or ""}">{i["value"]}</div></div>'
        for i in items
    )
    st.markdown(f'<div class="ledger-row">{cells}</div>', unsafe_allow_html=True)


def plotly_theme():
    return dict(
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        margin=dict(t=40, b=40, l=50, r=60),
        xaxis=dict(gridcolor=BORDER, zeroline=False),
        yaxis=dict(gridcolor=BORDER, zeroline=False),
    )


def display_fault_label(raw: str) -> str:
    """VALUE_MISMATCH -> Value mismatch — for chart/table display only, never for filtering."""
    return raw.replace("_", " ").capitalize()