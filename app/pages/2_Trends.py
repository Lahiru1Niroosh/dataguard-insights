import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.queries.trends import get_rolling_integrity, get_month_over_month_impact, get_fault_type_distribution

st.set_page_config(layout="wide")
st.title("Trends")

ACCENT = "#2E5EAA"
MUTED = "#AAB7C4"

# --- Integrity over time ---
st.subheader("Integrity % Over Time")
integrity_df = get_rolling_integrity()

if not integrity_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=integrity_df["started_at"], y=integrity_df["integrity_pct"],
        mode="lines+markers", name="Integrity %",
        line=dict(color=MUTED, width=1.5), marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=integrity_df["started_at"], y=integrity_df["rolling_avg_integrity_pct"],
        mode="lines", name="Rolling Avg",
        line=dict(color=ACCENT, width=3),
    ))
    fig.update_layout(
        template="plotly_white", height=380,
        yaxis_title="Integrity %", xaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=10, l=10, r=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No integrity data yet.")

# --- Month-over-month dollar impact ---
st.subheader("Dollar Impact by Month")
mom_df = get_month_over_month_impact()

if not mom_df.empty:
    mom_df["month_label"] = mom_df["month"].dt.strftime("%b %Y")
    fig2 = px.bar(
        mom_df, x="month_label", y="total_dollar_impact",
        text=mom_df["total_dollar_impact"].map(lambda v: f"${v:,.0f}"),
        color_discrete_sequence=[ACCENT],
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        template="plotly_white", height=350,
        yaxis_title="Dollar Impact ($)", xaxis_title=None,
        margin=dict(t=20, b=10, l=10, r=10),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

    if mom_df["pct_change"].notna().any():
        latest_change = mom_df["pct_change"].iloc[-1]
        direction = "up" if latest_change > 0 else "down"
        st.caption(f"Dollar impact is {direction} {abs(latest_change):.1f}% vs. the prior month.")
    else:
        st.caption("Not enough monthly history yet to compute a month-over-month change.")
else:
    st.info("No dollar impact data yet.")

# --- Fault type distribution over time ---
st.subheader("Fault Type Composition by Run")
fault_df = get_fault_type_distribution()

if not fault_df.empty:
    fault_df["run_label"] = "Run " + fault_df["run_id"].astype(str)
    fig3 = px.bar(
        fault_df, x="run_label", y="count", color="fault_type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig3.update_layout(
        template="plotly_white", height=400,
        yaxis_title="Discrepancy Count", xaxis_title=None,
        legend_title_text="Fault Type",
        margin=dict(t=20, b=10, l=10, r=10),
        barmode="stack",
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No fault type data yet.")