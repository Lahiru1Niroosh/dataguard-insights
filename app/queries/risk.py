"""
Phase B2 — Risk analytics.
Top-N accounts ranked by cumulative dollar impact.
"""
from app.db import run_query


def get_top_accounts_by_impact(top_n: int = 10) -> "pd.DataFrame":
    sql = """
        SELECT
            account_id,
            COUNT(*) AS discrepancy_count,
            SUM(dollar_impact) AS total_dollar_impact,
            RANK() OVER (ORDER BY SUM(dollar_impact) DESC) AS impact_rank
        FROM dataguard_meta.discrepancies
        WHERE account_id IS NOT NULL
        GROUP BY account_id
        ORDER BY total_dollar_impact DESC
        LIMIT %(top_n)s
    """
    return run_query(sql, params={"top_n": top_n})