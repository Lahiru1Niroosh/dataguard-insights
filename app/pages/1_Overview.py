import streamlit as st
import plotly.graph_objects as go
from app.queries.trends import get_run_history

st.set_page_config(layout="wide")
st.title("Overview")

ACCENT = "#2E5EAA"
GOOD = "#2E8B57"
BAD = "#C0392B"

df = get_run_history()

if df.empty:
    st.warning("No runs with recorded row counts yet.")
else:
    latest = df.iloc[-1]

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest["integrity_pct"],
        number={"suffix": "%", "font": {"size": 48}},
        title={"text": "Data Integrity (Latest Run)", "font": {"size": 18}},
        gauge={
            "axis": {"range": [95, 100], "tickwidth": 1},
            "bar": {"color": ACCENT},
            "steps": [
                {"range": [95, 98], "color": "#FADBD8"},
                {"range": [98, 99.5], "color": "#FCF3CF"},
                {"range": [99.5, 100], "color": "#D5F5E3"},
            ],
            "threshold": {
                "line": {"color": BAD, "width": 3},
                "thickness": 0.85,
                "value": 99.5,
            },
        },
    ))
    gauge.update_layout(height=280, margin=dict(t=40, b=10, l=30, r=30))

    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(gauge, use_container_width=True)
    with col2:
        k1, k2, k3 = st.columns(3)
        k1.metric("Discrepancies (latest run)", int(latest["discrepancy_count"]))
        k2.metric("Dollar Impact (latest run)", f"${latest['dollar_impact']:,.0f}")
        k3.metric("Total Runs Tracked", len(df))

        st.markdown("##### Run History")
        st.dataframe(
            df.style.format({
                "dollar_impact": "${:,.2f}",
                "integrity_pct": "{:.2f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )