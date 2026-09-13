import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.queries.trends import get_rolling_integrity, get_impact_trend, get_fault_type_distribution
from app.theme import inject_base_styles, plotly_theme, display_fault_label, TEAL, GOLD

st.set_page_config(layout="wide")
inject_base_styles()
st.title("Trends")
st.markdown('<div class="hero-accent"></div>', unsafe_allow_html=True)

st.subheader("Integrity % Over Time")
integrity_df = get_rolling_integrity()
if not integrity_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=integrity_df["started_at"], y=integrity_df["integrity_pct"],
                              mode="lines+markers", name="Integrity %",
                              line=dict(color="#8B96A5", width=1.5), marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=integrity_df["started_at"], y=integrity_df["rolling_avg_integrity_pct"],
                              mode="lines", name="Rolling avg", line=dict(color=TEAL, width=3)))
    fig.update_layout(height=380, hovermode="x unified",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                       **plotly_theme())
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No integrity data yet.")

st.subheader("Dollar Impact Over Time")
impact_df = get_impact_trend(granularity="day")
if not impact_df.empty:
    impact_df["bucket_label"] = impact_df["bucket"].dt.strftime("%b %d")
    fig2 = px.bar(impact_df, x="bucket_label", y="total_dollar_impact",
                  text=impact_df["total_dollar_impact"].map(lambda v: f"${v:,.0f}"),
                  color_discrete_sequence=[GOLD])
    fig2.update_traces(textposition="outside", cliponaxis=False)
    fig2.update_layout(height=350, showlegend=False, **plotly_theme())
    st.plotly_chart(fig2, use_container_width=True)
    latest_change = impact_df["pct_change"].iloc[-1]
    if latest_change is not None and latest_change == latest_change:  # None/NaN check
        direction = "up" if latest_change > 0 else "down"
        st.caption(f"Dollar impact is {direction} {abs(latest_change):.1f}% vs. the prior day.")
else:
    st.info("No dollar impact data yet.")

st.subheader("Fault Type Composition by Run")
fault_df = get_fault_type_distribution()
if not fault_df.empty:
    fault_df["run_label"] = "Run " + fault_df["run_seq"].astype(str)
    fault_df["fault_display"] = fault_df["fault_type"].map(display_fault_label)
    run_order = fault_df.sort_values("run_seq")["run_label"].unique().tolist()
    fig3 = px.bar(fault_df, x="run_label", y="count", color="fault_display",
                  category_orders={"run_label": run_order},
                  color_discrete_sequence=px.colors.qualitative.Prism)
    fig3.update_layout(height=400, legend_title_text="Fault type", barmode="stack", **plotly_theme())
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No fault type data yet.")