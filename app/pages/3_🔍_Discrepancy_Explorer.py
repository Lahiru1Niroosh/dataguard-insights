import streamlit as st
import plotly.express as px
from app.queries.trends import get_discrepancy_detail
from app.queries.risk import get_top_accounts_by_impact
from app.theme import (
    inject_base_styles, plotly_theme, display_fault_label, ledger_row,
    hero, section_header,
    RED, GOLD, TEAL, MUTED_TEXT, BORDER, TEXT,
)

st.set_page_config(layout="wide")
inject_base_styles()

# ---------------- Hero ----------------
hero(
    eyebrow="DataGuard Core · Explorer",
    title="Discrepancy Explorer",
    lede=(
        "Row-level drill-down into every recorded discrepancy — filter by fault "
        "type and run, quantify the dollar impact, and surface the accounts "
        "carrying the most exposure."
    ),
    meta_html=(
        "<div>Scope</div>"
        "<div><strong>all recorded discrepancies</strong></div>"
        "<div style='margin-top:0.6rem;'>Ranking</div>"
        "<div><strong>by cumulative dollar impact</strong></div>"
    ),
)

# ---------------- Data ----------------
df = get_discrepancy_detail()

if df.empty:
    st.markdown(
        '<div style="border:1px dashed #2A3340;border-radius:14px;'
        'padding:3rem;text-align:center;color:#8B96A5;font-size:0.95rem;">'
        'No discrepancies recorded yet.'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    df["fault_display"] = df["fault_type"].map(display_fault_label)
    df["run_label"] = "Run " + df["run_seq"].astype(str)

    # ============================================================
    # Filter + impact summary
    # ============================================================
    section_header("Filter & impact", "narrow the population")

    with st.container(border=True):
        col1, col2 = st.columns([1, 3], gap="large")

        with col1:
            st.markdown(
                '<div class="ledger-label" style="margin-bottom:0.75rem;">'
                'Filters</div>',
                unsafe_allow_html=True,
            )
            fault_types = st.multiselect(
                "Fault type",
                options=sorted(df["fault_display"].unique()),
                placeholder="All fault types",
            )
            run_labels = st.multiselect(
                "Run",
                options=sorted(
                    df["run_label"].unique(),
                    key=lambda x: int(x.split()[1]),
                    reverse=True,
                ),
                placeholder="All runs",
            )

        # --- filter application (unchanged logic) ---
        filtered = df.copy()
        if fault_types:
            filtered = filtered[filtered["fault_display"].isin(fault_types)]
        if run_labels:
            filtered = filtered[filtered["run_label"].isin(run_labels)]

        with col2:
            ledger_row([
                {"label": "Discrepancies matching filters",
                 "value": f"{len(filtered):,}"},
                {"label": "Dollar impact",
                 "value": f"${filtered['dollar_impact'].sum():,.0f}",
                 "accent": "gold"},
                {"label": "Accounts affected",
                 "value": f"{filtered['account_id'].nunique():,}"},
            ])

            summary = (
                filtered
                .groupby("fault_display", as_index=False)["dollar_impact"]
                .sum()
                .sort_values("dollar_impact")
            )
            fig = px.bar(
                summary,
                x="dollar_impact",
                y="fault_display",
                orientation="h",
                text=summary["dollar_impact"].map(lambda v: f"${v:,.0f}"),
                color_discrete_sequence=[RED],
            )
            fig.update_traces(
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
                textfont=dict(family="Inter, sans-serif", size=12, color=MUTED_TEXT),
            )
            fig.update_xaxes(
                range=[0, summary["dollar_impact"].max() * 1.2],
                tickprefix="$",
                tickformat=",.0f",
            )
            fig.update_yaxes(title=None)
            fig.update_layout(
                height=260,
                xaxis_title=None,
                **plotly_theme(),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("&nbsp;")

    # ============================================================
    # Detail table
    # ============================================================
    section_header("Discrepancy detail", f"{len(filtered):,} rows")

    with st.container(border=True):
        st.dataframe(
            filtered[[
                "run_label", "started_at", "table_name",
                "fault_display", "dollar_impact", "account_id",
            ]]
            .rename(columns={
                "run_label": "Run",
                "started_at": "Started",
                "table_name": "Table",
                "fault_display": "Fault Type",
                "dollar_impact": "Dollar Impact",
                "account_id": "Account",
            })
            .style.format({"Dollar Impact": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("&nbsp;")

    # ============================================================
    # Top accounts at risk
    # ============================================================
    section_header("Top accounts at risk", "by cumulative dollar impact")
    st.markdown(
        '<div style="color:#8B96A5;font-size:0.86rem;margin:-0.4rem 0 0.9rem 0;">'
        'Ranked by cumulative dollar impact across all discrepancies for that account.'
        '</div>',
        unsafe_allow_html=True,
    )

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
                ranked,
                x="total_dollar_impact",
                y="account_label",
                orientation="h",
                text=ranked["total_dollar_impact"].map(lambda v: f"${v:,.0f}"),
            )
            fig_risk.update_traces(
                textposition="outside",
                cliponaxis=False,
                marker_color=ranked["severity_color"],
                marker_line_width=0,
                textfont=dict(family="Inter, sans-serif", size=12, color=MUTED_TEXT),
            )
            fig_risk.update_xaxes(
                range=[0, ranked["total_dollar_impact"].max() * 1.2],
                tickprefix="$",
                tickformat=",.0f",
            )
            fig_risk.update_yaxes(type="category", title=None)
            fig_risk.update_layout(
                height=400,
                xaxis_title=None,
                **plotly_theme(),
            )
            st.plotly_chart(fig_risk, use_container_width=True,
                            config={"displayModeBar": False})

            st.markdown(
                '<div style="color:#8B96A5;font-size:0.82rem;margin-top:0.4rem;">'
                'Darker red = top 3 accounts by exposure — worth investigating first.'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="border:1px dashed #2A3340;border-radius:14px;'
                'padding:2rem;text-align:center;color:#8B96A5;font-size:0.9rem;">'
                'No account-level risk data yet.'
                '</div>',
                unsafe_allow_html=True,
            )