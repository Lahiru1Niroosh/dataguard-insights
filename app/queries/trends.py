"""
Phase B2 — Trend analytics.
Rolling integrity %, month-over-month dollar impact change,
and discrepancy type distribution over time.
"""
from app.db import run_query


def get_run_history() -> "pd.DataFrame":
    """
    One row per run: run_id, started_at, total_rows_checked,
    discrepancy_count, dollar_impact, integrity_pct.
    Only includes runs that have total_rows_checked recorded
    (older runs before that column existed are excluded).
    """
    sql = """
        SELECT
            r.run_id,
            r.started_at,
            r.total_rows_checked,
            COUNT(d.id) AS discrepancy_count,
            COALESCE(SUM(d.dollar_impact), 0) AS dollar_impact,
            CASE
                WHEN r.total_rows_checked > 0
                THEN ROUND(100.0 * (1 - COUNT(d.id)::numeric / r.total_rows_checked), 2)
                ELSE NULL
            END AS integrity_pct
        FROM dataguard_meta.reconciliation_runs r
        LEFT JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
        WHERE r.total_rows_checked IS NOT NULL
        GROUP BY r.run_id, r.started_at, r.total_rows_checked
        ORDER BY r.started_at
    """
    return run_query(sql)


def get_rolling_integrity(window_runs: int = 7) -> "pd.DataFrame":
    """
    Rolling average integrity % over the last N runs (a proxy for
    '7/30-day' since our demo runs happen much faster than daily).
    """
    sql = f"""
        WITH run_stats AS (
            SELECT
                r.run_id,
                r.started_at,
                CASE
                    WHEN r.total_rows_checked > 0
                    THEN 100.0 * (1 - COUNT(d.id)::numeric / r.total_rows_checked)
                    ELSE NULL
                END AS integrity_pct
            FROM dataguard_meta.reconciliation_runs r
            LEFT JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
            WHERE r.total_rows_checked IS NOT NULL
            GROUP BY r.run_id, r.started_at, r.total_rows_checked
        )
        SELECT
            run_id,
            started_at,
            ROUND(integrity_pct, 2) AS integrity_pct,
            ROUND(AVG(integrity_pct) OVER (
                ORDER BY started_at
                ROWS BETWEEN {window_runs - 1} PRECEDING AND CURRENT ROW
            ), 2) AS rolling_avg_integrity_pct
        FROM run_stats
        ORDER BY started_at
    """
    return run_query(sql)


def get_month_over_month_impact() -> "pd.DataFrame":
    """
    Month-over-month % change in total dollar impact, using LAG().
    With a young dataset this may only show 1 month — that's expected
    and will fill in as more runs accumulate over time.
    """
    sql = """
        WITH monthly AS (
            SELECT
                DATE_TRUNC('month', r.started_at) AS month,
                SUM(d.dollar_impact) AS total_dollar_impact
            FROM dataguard_meta.reconciliation_runs r
            JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
            GROUP BY DATE_TRUNC('month', r.started_at)
        )
        SELECT
            month,
            total_dollar_impact,
            LAG(total_dollar_impact) OVER (ORDER BY month) AS prev_month_impact,
            ROUND(
                100.0 * (total_dollar_impact - LAG(total_dollar_impact) OVER (ORDER BY month))
                / NULLIF(LAG(total_dollar_impact) OVER (ORDER BY month), 0),
                2
            ) AS pct_change
        FROM monthly
        ORDER BY month
    """
    return run_query(sql)


def get_fault_type_distribution() -> "pd.DataFrame":
    """Discrepancy type distribution over time (pivot-style, one row per run/fault_type)."""
    sql = """
        SELECT
            r.run_id,
            r.started_at,
            d.fault_type,
            COUNT(*) AS count
        FROM dataguard_meta.reconciliation_runs r
        JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
        GROUP BY r.run_id, r.started_at, d.fault_type
        ORDER BY r.started_at, d.fault_type
    """
    return run_query(sql)