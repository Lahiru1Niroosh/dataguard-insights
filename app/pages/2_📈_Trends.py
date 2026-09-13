import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.queries.trends import get_rolling_integrity, get_impact_trend, get_fault_type_distribution
from app.theme import (
    inject_base_styles, plotly_theme, display_fault_label,
    hero, section_header,
    TEAL, GOLD, RED, MUTED_TEXT, BORDER, TEXT, PANEL,
)

st.set_page_config(layout="wide")
inject_base_styles()

# ---------------- Hero ----------------
hero(
    eyebrow="DataGuard Core · Trends",
    title="Trends",
    lede=(
        "Integrity, dollar exposure, and fault-type composition across every "
        "recorded reconciliation run — the longitudinal view behind the "
        "latest-run snapshot on the home page."
    ),
    meta_html=(
        "<div>Window</div>"
        "<div><strong>all recorded runs</strong></div>"
        "<div style='margin-top:0.6rem;'>Granularity</div>"
        "<div><strong>per run · per day</strong></div>"
    ),
)

# ============================================================
# Integrity over time
# ============================================================
section_header("Integrity % over time", "actual vs. rolling average")

integrity_df = get_rolling_integrity()
if not integrity_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=integrity_df["started_at"],
        y=integrity_df["integrity_pct"],
        mode="lines+markers",
        name="Integrity %",
        line=dict(color="#8B96A5", width=1.5),
        marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=integrity_df["started_at"],
        y=integrity_df["rolling_avg_integrity_pct"],
        mode="lines",
        name="Rolling avg",
        line=dict(color=TEAL, width=3),
    ))
    fig.update_layout(
        height=400,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color=MUTED_TEXT),
        ),
        **plotly_theme(),
    )
    fig.update_yaxes(ticksuffix="%", range=[95, 100])
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.markdown(
        '<div style="border:1px dashed #2A3340;border-radius:14px;'
        'padding:2.5rem;text-align:center;color:#8B96A5;font-size:0.95rem;">'
        'No integrity data yet.'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("&nbsp;")

# ============================================================
# Dollar impact over time
# ============================================================
section_header("Dollar impact over time", "daily aggregate")

impact_df = get_impact_trend(granularity="day")
if not impact_df.empty:
    impact_df["bucket_label"] = impact_df["bucket"].dt.strftime("%b %d")

    fig2 = px.bar(
        impact_df,
        x="bucket_label",
        y="total_dollar_impact",
        text=impact_df["total_dollar_impact"].map(lambda v: f"${v:,.0f}"),
        color_discrete_sequence=[GOLD],
    )
    fig2.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        textfont=dict(family="Inter, sans-serif", size=12, color=MUTED_TEXT),
    )
    fig2.update_layout(
        height=380,
        showlegend=False,
        bargap=0.35,
        **plotly_theme(),
    )
    fig2.update_yaxes(tickprefix="$", tickformat=",.0f")

    with st.container(border=True):
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    latest_change = impact_df["pct_change"].iloc[-1]
    if latest_change is not None and latest_change == latest_change:  # None/NaN check
        direction = "up" if latest_change > 0 else "down"
        arrow = "▲" if latest_change > 0 else "▼"
        color = RED if latest_change > 0 else TEAL
        st.markdown(
            f'<div style="margin-top:0.6rem;color:#8B96A5;font-size:0.86rem;">'
            f'Dollar impact is <span style="color:{color};font-weight:600;">'
            f'{arrow} {direction} {abs(latest_change):.1f}%</span> '
            f'vs. the prior day.'
            f'</div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<div style="border:1px dashed #2A3340;border-radius:14px;'
        'padding:2.5rem;text-align:center;color:#8B96A5;font-size:0.95rem;">'
        'No dollar impact data yet.'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("&nbsp;")

# ============================================================
# Fault type composition
# ============================================================
section_header("Fault type composition by run", "stacked counts")

fault_df = get_fault_type_distribution()
if not fault_df.empty:
    fault_df["run_label"] = "Run " + fault_df["run_seq"].astype(str)
    fault_df["fault_display"] = fault_df["fault_type"].map(display_fault_label)
    run_order = fault_df.sort_values("run_seq")["run_label"].unique().tolist()

    # Ledger palette for fault types — deliberately restrained, not Prism
    fault_palette = ["#3FA796", "#C9A227", "#D64545", "#8B96A5", "#6E7F94", "#4A5A6E"]

    fig3 = px.bar(
        fault_df,
        x="run_label",
        y="count",
        color="fault_display",
        category_orders={"run_label": run_order},
        color_discrete_sequence=fault_palette,
    )
    fig3.update_traces(marker_line_width=0)
    fig3.update_layout(
        height=420,
        barmode="stack",
        bargap=0.35,
        legend=dict(
            title=dict(text="Fault type", font=dict(size=12, color=MUTED_TEXT)),
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color=TEXT),
        ),
        **plotly_theme(),
    )

    with st.container(border=True):
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
else:
    st.markdown(
        '<div style="border:1px dashed #2A3340;border-radius:14px;'
        'padding:2.5rem;text-align:center;color:#8B96A5;font-size:0.95rem;">'
        'No fault type data yet.'
        '</div>',
        unsafe_allow_html=True,
    )