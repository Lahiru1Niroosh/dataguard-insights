"""
Phase B5 — Data-driven executive summary generator.
Converts the latest run's actual numbers into a templated,
decision-ready natural-language summary. Every number in the
sentence comes from a real query — nothing hardcoded.
"""
from app.db import run_query


def get_latest_run_summary() -> dict:
    latest_sql = """
        SELECT r.run_id, r.started_at, r.total_rows_checked,
               COUNT(d.id) AS discrepancy_count,
               COALESCE(SUM(d.dollar_impact), 0) AS dollar_impact
        FROM dataguard_meta.reconciliation_runs r
        LEFT JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
        WHERE r.total_rows_checked IS NOT NULL AND r.started_at IS NOT NULL
        GROUP BY r.run_id, r.started_at, r.total_rows_checked
        ORDER BY r.started_at DESC
        LIMIT 1
    """
    latest = run_query(latest_sql)
    if latest.empty:
        return {}

    latest_row = latest.iloc[0]
    run_id = int(latest_row["run_id"])
    started_at = latest_row["started_at"]  # used to find "prior" — never use run_id for this

    accounts_sql = """
        SELECT COUNT(DISTINCT account_id) AS affected_accounts
        FROM dataguard_meta.discrepancies
        WHERE run_id = %(run_id)s AND account_id IS NOT NULL
    """
    accounts = run_query(accounts_sql, params={"run_id": run_id})
    affected_accounts = int(accounts.iloc[0]["affected_accounts"]) if not accounts.empty else 0

    top_fault_sql = """
        SELECT fault_type, COUNT(*) AS cnt
        FROM dataguard_meta.discrepancies
        WHERE run_id = %(run_id)s
        GROUP BY fault_type
        ORDER BY cnt DESC
        LIMIT 1
    """
    top_fault = run_query(top_fault_sql, params={"run_id": run_id})
    top_fault_type = top_fault.iloc[0]["fault_type"] if not top_fault.empty else None

    prior_sql = """
        SELECT COALESCE(SUM(d.dollar_impact), 0) AS dollar_impact
        FROM dataguard_meta.reconciliation_runs r
        LEFT JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
        WHERE r.total_rows_checked IS NOT NULL
          AND r.started_at IS NOT NULL
          AND r.started_at < %(started_at)s
        GROUP BY r.run_id, r.started_at
        ORDER BY r.started_at DESC
        LIMIT 1
    """
    prior = run_query(prior_sql, params={"started_at": started_at})

    pct_change = None
    if not prior.empty and prior.iloc[0]["dollar_impact"] > 0:
        prior_impact = float(prior.iloc[0]["dollar_impact"])
        current_impact = float(latest_row["dollar_impact"])
        pct_change = round(100 * (current_impact - prior_impact) / prior_impact, 1)

    total_rows = latest_row["total_rows_checked"]
    integrity_pct = (
        round(100.0 * (1 - latest_row["discrepancy_count"] / total_rows), 2)
        if total_rows else None
    )

    return {
        "run_id": run_id,
        "discrepancy_count": int(latest_row["discrepancy_count"]),
        "dollar_impact": float(latest_row["dollar_impact"]),
        "affected_accounts": affected_accounts,
        "top_fault_type": top_fault_type,
        "pct_change": pct_change,
        "integrity_pct": integrity_pct,
    }


def generate_summary_text() -> str:
    data = get_latest_run_summary()
    if not data:
        return "No run data available yet."

    sentence = (
        f"This run flagged {data['discrepancy_count']} discrepancies "
        f"totaling ${data['dollar_impact']:,.2f} across {data['affected_accounts']} accounts"
    )

    if data["pct_change"] is not None:
        direction = "an increase" if data["pct_change"] > 0 else "a decrease"
        sentence += f", {direction} of {abs(data['pct_change'])}% from the prior run"

    if data["top_fault_type"]:
        sentence += f", concentrated primarily in {data['top_fault_type'].replace('_', ' ').lower()}"

    sentence += "."
    return sentence