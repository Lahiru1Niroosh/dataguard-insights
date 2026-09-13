import streamlit as st
import plotly.express as px
from app.queries.trends import get_discrepancy_detail
from app.queries.risk import get_top_accounts_by_impact
from app.theme import inject_base_styles, plotly_theme, display_fault_label, ledger_row, RED

st.set_page_config(layout="wide")
inject_base_styles()
st.title("Discrepancy Explorer")
st.markdown('<div class="hero-accent"></div>', unsafe_allow_html=True)

df = get_discrepancy_detail()

if df.empty:
    st.info("No discrepancies recorded yet.")
else:
    df["fault_display"] = df["fault_type"].map(display_fault_label)
    df["run_label"] = "Run " + df["run_seq"].astype(str)

    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("##### Filters")
            fault_types = st.multiselect("Fault type", options=sorted(df["fault_display"].unique()))
            run_labels = st.multiselect(
                "Run",
                options=sorted(df["run_label"].unique(), key=lambda x: int(x.split()[1]), reverse=True),
            )

        filtered = df.copy()
        if fault_types:
            filtered = filtered[filtered["fault_display"].isin(fault_types)]
        if run_labels:
            filtered = filtered[filtered["run_label"].isin(run_labels)]

        with col2:
            ledger_row([
                {"label": "Discrepancies matching filters", "value": f"{len(filtered):,}"},
                {"label": "Dollar impact", "value": f"${filtered['dollar_impact'].sum():,.0f}", "accent": "gold"},
                {"label": "Accounts affected", "value": f"{filtered['account_id'].nunique():,}"},
            ])

            summary = filtered.groupby("fault_display", as_index=False)["dollar_impact"].sum().sort_values("dollar_impact")
            fig = px.bar(
                summary, x="dollar_impact", y="fault_display", orientation="h",
                text=summary["dollar_impact"].map(lambda v: f"${v:,.0f}"),
                color_discrete_sequence=[RED],
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(range=[0, summary["dollar_impact"].max() * 1.2])
            fig.update_layout(height=240, yaxis_title=None, xaxis_title="Dollar impact ($)", **plotly_theme())
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Discrepancy Detail")
    st.dataframe(
        filtered[["run_label", "started_at", "table_name", "fault_display", "dollar_impact", "account_id"]]
        .rename(columns={"run_label": "Run", "started_at": "Started", "table_name": "Table",
                          "fault_display": "Fault Type", "dollar_impact": "Dollar Impact", "account_id": "Account"})
        .style.format({"Dollar Impact": "${:,.2f}"}),
        use_container_width=True, hide_index=True,
    )

    st.markdown('<div class="hero-accent"></div>', unsafe_allow_html=True)
    st.subheader("Top Accounts at Risk")
    st.caption("Ranked by cumulative dollar impact across all discrepancies for that account.")

    with st.container(border=True):
        top_accounts = get_top_accounts_by_impact(top_n=10)
        if not top_accounts.empty:
            ranked = top_accounts.sort_values("total_dollar_impact", ascending=True).copy()
            ranked["account_label"] = "Account " + ranked["account_id"].astype(str)
            ranked["severity_color"] = [
                RED if rank <= 3 else "#8B4A4A"
                for rank in ranked["impact_rank"]
            ]

            fig_risk = px.bar(
                ranked, x="total_dollar_impact", y="account_label", orientation="h",
                text=ranked["total_dollar_impact"].map(lambda v: f"${v:,.0f}"),
            )
            fig_risk.update_traces(textposition="outside", cliponaxis=False, marker_color=ranked["severity_color"])
            fig_risk.update_xaxes(range=[0, ranked["total_dollar_impact"].max() * 1.2])
            fig_risk.update_yaxes(type="category")
            fig_risk.update_layout(height=380, yaxis_title=None, xaxis_title="Cumulative dollar impact ($)", **plotly_theme())
            st.plotly_chart(fig_risk, use_container_width=True)
            st.caption("Darker red = top 3 accounts by exposure — worth investigating first.")