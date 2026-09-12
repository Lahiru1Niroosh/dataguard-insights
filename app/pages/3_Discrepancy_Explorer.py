import streamlit as st
import plotly.express as px
from app.db import run_query

st.set_page_config(layout="wide")
st.title("Discrepancy Explorer")

df = run_query("""
    SELECT r.run_id, r.started_at, d.table_name, d.fault_type, d.dollar_impact, d.account_id
    FROM dataguard_meta.discrepancies d
    JOIN dataguard_meta.reconciliation_runs r ON r.run_id = d.run_id
    ORDER BY r.started_at DESC
""")

if df.empty:
    st.info("No discrepancies recorded yet.")
else:
    col1, col2 = st.columns([1, 3])
    with col1:
        fault_types = st.multiselect("Fault type", options=sorted(df["fault_type"].unique()))
        run_ids = st.multiselect("Run", options=sorted(df["run_id"].unique(), reverse=True))

    filtered = df.copy()
    if fault_types:
        filtered = filtered[filtered["fault_type"].isin(fault_types)]
    if run_ids:
        filtered = filtered[filtered["run_id"].isin(run_ids)]

    with col2:
        summary = filtered.groupby("fault_type", as_index=False)["dollar_impact"].sum().sort_values("dollar_impact", ascending=True)
        fig = px.bar(
            summary, x="dollar_impact", y="fault_type", orientation="h",
            text=summary["dollar_impact"].map(lambda v: f"${v:,.0f}"),
            color_discrete_sequence=["#2E5EAA"],
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            template="plotly_white", height=280,
            xaxis_title="Dollar Impact ($)", yaxis_title=None,
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**{len(filtered):,} discrepancies** matching current filters")
    st.dataframe(
        filtered.style.format({"dollar_impact": "${:,.2f}"}),
        use_container_width=True,
        hide_index=True,
    )