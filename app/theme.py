"""
Shared visual identity for DataGuard Insights: an "audit ledger"
aesthetic, not a generic dark SaaS dashboard. One place to change
color/type for the whole app.
"""
import streamlit as st

INK = "#0B0F14"
PANEL = "#131A24"
PANEL_2 = "#0F1620"
BORDER = "#2A3340"
BORDER_SOFT = "#1E2632"
TEXT = "#E8E6DE"
MUTED_TEXT = "#8B96A5"
TEAL = "#3FA796"      # verified / passing state
RED = "#D64545"       # discrepancy / risk
GOLD = "#C9A227"      # one hero number per page, used sparingly


def inject_base_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&display=swap');

    /* ============================== Base ============================== */
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    .stApp {{
        background:
            radial-gradient(1100px 520px at 8% -8%,  rgba(63,167,150,0.07), transparent 60%),
            radial-gradient(900px  480px at 100% 0%, rgba(201,162,39,0.055), transparent 55%),
            {INK};
    }}

    /* Kill default Streamlit top padding so hero sits higher */
    .block-container {{
        padding-top: 2.25rem !important;
        padding-bottom: 5rem !important;
        padding-left: 2.75rem !important;
        padding-right: 2.75rem !important;
        max-width: 1440px !important;
    }}

    /* ============================== Type ============================== */
    h1, h2, h3, h4 {{
        font-family: 'Source Serif 4', serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: {TEXT};
    }}
    h1 {{ font-size: 2.75rem !important; line-height: 1.05 !important; margin-bottom: 0.25rem !important; }}
    h2 {{ font-size: 1.75rem !important; }}
    h3 {{ font-size: 1.25rem !important; }}
    h4 {{ font-size: 1.05rem !important; }}

    p, .stMarkdown p {{ color: {TEXT}; }}

    /* ============================== Eyebrow / hero ============================== */
    .dg-eyebrow {{
        color: {MUTED_TEXT};
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.55rem;
    }}
    .dg-hero {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid {BORDER_SOFT};
        margin-bottom: 1.75rem;
    }}
    .dg-hero-title {{
        font-family: 'Source Serif 4', serif;
        font-weight: 700;
        font-size: 2.75rem;
        line-height: 1.05;
        letter-spacing: -0.02em;
        color: {TEXT};
        margin: 0;
    }}
    .dg-hero-lede {{
        color: {MUTED_TEXT};
        font-size: 1.02rem;
        line-height: 1.6;
        max-width: 62ch;
        margin-top: 0.85rem;
    }}
    .dg-hero-meta {{
        text-align: right;
        color: {MUTED_TEXT};
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        line-height: 1.6;
        white-space: nowrap;
        padding-top: 0.5rem;
    }}
    .dg-hero-meta strong {{ color: {TEXT}; font-weight: 600; }}

    .hero-accent {{
        height: 3px;
        width: 84px;
        background: linear-gradient(90deg, {GOLD}, {TEAL});
        border-radius: 2px;
        margin: 0.85rem 0 1rem 0;
    }}

    /* ============================== Section heading ============================== */
    .dg-section {{
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 1rem;
        margin: 2rem 0 0.75rem 0;
    }}
    .dg-section-title {{
        font-family: 'Source Serif 4', serif;
        font-weight: 700;
        font-size: 1.35rem;
        letter-spacing: -0.015em;
        color: {TEXT};
    }}
    .dg-section-note {{
        color: {MUTED_TEXT};
        font-size: 0.78rem;
        letter-spacing: 0.02em;
    }}

    /* ============================== Ledger row ============================== */
    .ledger-row {{
        display: flex;
        align-items: center;
        border-top: 1px solid {BORDER};
        border-bottom: 1px solid {BORDER};
        padding: 1.5rem 0;
        margin: 0.5rem 0 0 0;
        background: linear-gradient(180deg, rgba(255,255,255,0.014), transparent);
    }}
    .ledger-row > div {{
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 0 1.5rem;
        border-right: 1px solid {BORDER};
        min-width: 0;
    }}
    .ledger-row > div:first-child {{ padding-left: 0; }}
    .ledger-row > div:last-child  {{ border-right: none; padding-right: 0; }}

    .ledger-label {{
        color: {MUTED_TEXT};
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.55rem;
        font-weight: 600;
        margin: 0 0 0.55rem 0;
    }}
    .ledger-value {{
        font-variant-numeric: tabular-nums;
        font-weight: 700;
        font-size: 2.05rem;
        line-height: 1.05;
        color: {TEXT};
        word-break: break-word;
        font-family: 'Source Serif 4', serif;
        letter-spacing: -0.015em;
        margin: 0;
    }}
    .ledger-value.gold {{ color: {GOLD}; }}
    .ledger-value.red  {{ color: {RED}; }}
    .ledger-value.teal {{ color: {TEAL}; }}

    /* ============================== Status pill ============================== */
    .status-pill {{
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        vertical-align: middle;
    }}
    .status-pill.ok {{
        background: rgba(63,167,150,0.14);
        color: {TEAL};
        border: 1px solid rgba(63,167,150,0.45);
        box-shadow: 0 0 0 3px rgba(63,167,150,0.06);
    }}
    .status-pill.warn {{
        background: rgba(214,69,69,0.14);
        color: {RED};
        border: 1px solid rgba(214,69,69,0.45);
        box-shadow: 0 0 0 3px rgba(214,69,69,0.06);
    }}

    /* ============================== Cards ============================== */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {BORDER} !important;
        border-radius: 14px !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.0) 160px), {PANEL};
        box-shadow:
            0 1px 0 rgba(255,255,255,0.03) inset,
            0 12px 32px -22px rgba(0,0,0,0.9);
        padding: 1.25rem 1.25rem !important;
    }}

    /* ============================== Dataframe ============================== */
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}
    [data-testid="stDataFrame"] thead th {{
        background: {PANEL_2} !important;
        color: {MUTED_TEXT} !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.68rem !important;
        font-weight: 600 !important;
    }}

    /* ============================== Sidebar ============================== */
    [data-testid="stSidebar"] {{
        background: {PANEL};
        border-right: 1px solid {BORDER};
        min-width: 250px !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 1.5rem; }}

    [data-testid="stSidebarNav"] {{ padding-top: 0.5rem; }}
    /* ============================================================
       Sidebar nav — force uniform styling across ALL entries
       ============================================================ */

    /* Container: remove default list chrome */
    [data-testid="stSidebarNav"] ul,
    [data-testid="stSidebarNav"] ol {{
        padding: 0 !important;
        margin: 0 !important;
        list-style: none !important;
    }}
    [data-testid="stSidebarNav"] li {{
        padding: 0 !important;
        margin: 0 !important;
        list-style: none !important;
    }}

    /* Every link — same base, no exceptions */
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNav"] a:link,
    [data-testid="stSidebarNav"] a:visited,
    [data-testid="stSidebarNav"] a:any-link {{
        display: flex !important;
        align-items: center !important;
        color: #8B96A5 !important;
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 0.45rem 0.85rem !important;
        margin: 0.15rem 0.5rem !important;
        font-size: 0.87rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em !important;
        text-decoration: none !important;
        box-shadow: none !important;
        outline: none !important;
        transition: background-color 120ms ease, color 120ms ease, border-color 120ms ease;
    }}

    /* Any child spans inside the link inherit the link color */
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] a p,
    [data-testid="stSidebarNav"] a div {{
        color: inherit !important;
        background: transparent !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        margin: 0 !important;
    }}

    /* Hover — identical for all items */
    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNav"] a:focus {{
        background-color: rgba(255,255,255,0.05) !important;
        color: #E8E6DE !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }}

    /* Active — one clear style, overriding EVERY possible marker */
    [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebarNav"] a[aria-selected="true"],
    [data-testid="stSidebarNav"] a[kind="primary"],
    [data-testid="stSidebarNav"] a[kind="secondary"],
    [data-testid="stSidebarNav"] a[class*="active"],
    [data-testid="stSidebarNav"] a[data-testid*="active"] {{
        background-color: rgba(63,167,150,0.13) !important;
        background-image: none !important;
        color: #3FA796 !important;
        border: 1px solid rgba(63,167,150,0.35) !important;
        box-shadow: none !important;
    }}

    /* Nuke Streamlit's default primary button fill that paints the active pill */
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebarNav"] button {{
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        color: inherit !important;
    }}

    /* Icon / emoji alignment — same for every row */
    [data-testid="stSidebarNav"] a img,
    [data-testid="stSidebarNav"] a svg,
    [data-testid="stSidebarNav"] a [data-testid*="Icon"],
    [data-testid="stSidebarNav"] a > span:first-child {{
        flex: 0 0 auto !important;
        width: 1.15rem !important;
        height: 1.15rem !important;
        margin-right: 0.6rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Last-resort: any element inside the nav that isn't matched above */
    [data-testid="stSidebarNav"] * {{
        box-shadow: none !important;
        background-image: none !important;
    }}
    [data-testid="stSidebarNav"] *[style*="background"] {{
        background: transparent !important;
    }}
    [data-testid="stSidebar"] footer {{ display: none !important; }}

    /* ============================== Top chrome off ============================== */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stAppDeployButton"],
    .stAppDeployButton,
    #MainMenu {{
        display: none !important;
        visibility: hidden !important;
    }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 0 !important;
    }}

    /* ============================== Misc ============================== */
    hr {{ border-color: {BORDER}; }}
    [data-testid="stCaptionContainer"], .stCaption {{ color: {MUTED_TEXT} !important; }}

    /* ============================================================
       Tighten Streamlit's default vertical rhythm — the biggest
       source of "long gaps" between cards/sections.
       ============================================================ */

    /* Base block gap */
    [data-testid="stVerticalBlock"] {{ gap: 0.35rem !important; }}
    [data-testid="stHorizontalBlock"] {{ gap: 0.75rem !important; }}

    /* Element container gap (wraps each widget) */
    [data-testid="stElementContainer"] {{ margin-bottom: 0 !important; }}

    /* Markdown paragraphs */
    .stMarkdown, [data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}
    .stMarkdown p {{ margin-bottom: 0.4rem !important; }}

    /* Kill the <br> / &nbsp; tax */
    .stMarkdown br {{ display: none; }}

    /* Card inner spacing */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        padding: 1.25rem 1.25rem !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] > div > div > div[data-testid="stVerticalBlock"] {{
        gap: 0.25rem !important;
    }}

    /* Section header tightened */
    .dg-section {{
        margin: 1.25rem 0 0.5rem 0 !important;
    }}

    /* Hero tightened */
    .dg-hero {{
        margin-bottom: 1.25rem !important;
        padding-bottom: 1.1rem !important;
    }}
    .hero-accent {{
        margin: 0.6rem 0 0.85rem 0 !important;
    }}

    /* Plotly chart wrapper */
    [data-testid="stPlotlyChart"] {{
        margin: 0 !important;
    }}

    /* DataFrame wrapper */
    [data-testid="stDataFrame"] {{
        margin-top: 0.25rem !important;
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


def hero(eyebrow: str, title: str, lede: str, meta_html: str = ""):
    """Display-only hero block. No logic, no data."""
    meta = (
        f'<div class="dg-hero-meta">{meta_html}</div>' if meta_html else ""
    )
    st.markdown(
        f'<div class="dg-hero">'
        f'  <div>'
        f'    <div class="dg-eyebrow">{eyebrow}</div>'
        f'    <div class="dg-hero-title">{title}</div>'
        f'    <div class="hero-accent"></div>'
        f'    <div class="dg-hero-lede">{lede}</div>'
        f'  </div>'
        f'  {meta}'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str = ""):
    """Display-only section heading with optional right-aligned note."""
    note_html = f'<div class="dg-section-note">{note}</div>' if note else ""
    st.markdown(
        f'<div class="dg-section">'
        f'  <div class="dg-section-title">{title}</div>'
        f'  {note_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def plotly_theme():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        margin=dict(t=44, b=44, l=52, r=64),
        hoverlabel=dict(
            bgcolor=INK,
            bordercolor=BORDER,
            font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        ),
        xaxis=dict(gridcolor=BORDER, zeroline=False, linecolor=BORDER,
                   ticks="outside", tickcolor=BORDER, ticklen=4),
        yaxis=dict(gridcolor=BORDER, zeroline=False, linecolor=BORDER,
                   ticks="outside", tickcolor=BORDER, ticklen=4),
    )


def display_fault_label(raw: str) -> str:
    """VALUE_MISMATCH -> Value mismatch — for chart/table display only, never for filtering."""
    return raw.replace("_", " ").capitalize()