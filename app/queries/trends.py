"""
Phase B2 — Trend analytics.
Every query here defines "valid run" the same way: total_rows_checked
IS NOT NULL. Ordering and "latest/prior" comparisons use started_at,
never run_id — run_id is a database sequence, not a timeline.
"""
from app.db import run_query


VALID_RUN_FILTER = "r.total_rows_checked IS NOT NULL AND r.started_at IS NOT NULL"


def get_run_history() -> "pd.DataFrame":
    """
    One row per valid run, in chronological order, with a run_seq
    column (1, 2, 3...) for display — never show raw run_id as an
    axis label, since run_id order can diverge from time order.
    """
    sql = f"""
        SELECT
            r.run_id,
            ROW_NUMBER() OVER (ORDER BY r.started_at) AS run_seq,
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
        WHERE {VALID_RUN_FILTER}
        GROUP BY r.run_id, r.started_at, r.total_rows_checked
        ORDER BY r.started_at
    """
    return run_query(sql)


def get_rolling_integrity(window_runs: int = 7) -> "pd.DataFrame":
    sql = f"""
        WITH run_stats AS (
            SELECT
                r.run_id,
                ROW_NUMBER() OVER (ORDER BY r.started_at) AS run_seq,
                r.started_at,
                CASE
                    WHEN r.total_rows_checked > 0
                    THEN 100.0 * (1 - COUNT(d.id)::numeric / r.total_rows_checked)
                    ELSE NULL
                END AS integrity_pct
            FROM dataguard_meta.reconciliation_runs r
            LEFT JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
            WHERE {VALID_RUN_FILTER}
            GROUP BY r.run_id, r.started_at, r.total_rows_checked
        )
        SELECT
            run_id, run_seq, started_at,
            ROUND(integrity_pct, 2) AS integrity_pct,
            ROUND(AVG(integrity_pct) OVER (
                ORDER BY started_at
                ROWS BETWEEN {window_runs - 1} PRECEDING AND CURRENT ROW
            ), 2) AS rolling_avg_integrity_pct
        FROM run_stats
        ORDER BY started_at
    """
    return run_query(sql)


def get_impact_trend(granularity: str = "day") -> "pd.DataFrame":
    """
    Dollar impact over time, bucketed by day or month, with a
    generated date spine so a genuinely clean period shows as
    $0 instead of silently disappearing from the trend (the old
    version used an INNER JOIN and DATE_TRUNC('month', ...) only —
    both wrong for a young, same-day dataset).
    Use 'day' until you have enough history for monthly buckets
    to mean anything (roughly 2+ months of real runs).
    """
    trunc_unit = "day" if granularity == "day" else "month"
    sql = f"""
        WITH bounds AS (
            SELECT MIN(started_at) AS min_ts, MAX(started_at) AS max_ts
            FROM dataguard_meta.reconciliation_runs r
            WHERE {VALID_RUN_FILTER}
        ),
        spine AS (
            SELECT generate_series(
                DATE_TRUNC('{trunc_unit}', min_ts),
                DATE_TRUNC('{trunc_unit}', max_ts),
                '1 {trunc_unit}'::interval
            ) AS bucket
            FROM bounds
        ),
        actuals AS (
            SELECT
                DATE_TRUNC('{trunc_unit}', r.started_at) AS bucket,
                COALESCE(SUM(d.dollar_impact), 0) AS total_dollar_impact
            FROM dataguard_meta.reconciliation_runs r
            LEFT JOIN dataguard_meta.discrepancies d ON d.run_id = r.run_id
            WHERE {VALID_RUN_FILTER}
            GROUP BY DATE_TRUNC('{trunc_unit}', r.started_at)
        )
        SELECT
            spine.bucket,
            COALESCE(actuals.total_dollar_impact, 0) AS total_dollar_impact,
            LAG(COALESCE(actuals.total_dollar_impact, 0)) OVER (ORDER BY spine.bucket) AS prev_bucket_impact,
            ROUND(
                100.0 * (COALESCE(actuals.total_dollar_impact, 0) - LAG(COALESCE(actuals.total_dollar_impact, 0)) OVER (ORDER BY spine.bucket))
                / NULLIF(LAG(COALESCE(actuals.total_dollar_impact, 0)) OVER (ORDER BY spine.bucket), 0),
                2
            ) AS pct_change
        FROM spine
        LEFT JOIN actuals ON actuals.bucket = spine.bucket
        ORDER BY spine.bucket
    """
    return run_query(sql)


def get_fault_type_distribution() -> "pd.DataFrame":
    """
    Discrepancy type distribution over time. run_seq is computed
    once per distinct run in a separate CTE, then joined in — computing
    it directly on the fault-type-grouped rows (the original bug) gave
    every (run, fault_type) pair its own sequence number instead of
    every run sharing one, fragmenting each run into several fake runs.
    """
    sql = f"""
        WITH run_order AS (
            SELECT DISTINCT r.run_id, r.started_at,
                   ROW_NUMBER() OVER (ORDER BY r.started_at) AS run_seq
            FROM dataguard_meta.reconciliation_runs r
            WHERE {VALID_RUN_FILTER}
        )
        SELECT
            ro.run_id,
            ro.run_seq,
            ro.started_at,
            d.fault_type,
            COUNT(*) AS count
        FROM run_order ro
        JOIN dataguard_meta.discrepancies d ON d.run_id = ro.run_id
        GROUP BY ro.run_id, ro.run_seq, ro.started_at, d.fault_type
        ORDER BY ro.started_at, d.fault_type
    """
    return run_query(sql)


def get_discrepancy_detail() -> "pd.DataFrame":
    """
    Row-level discrepancy detail joined to run_seq (never raw run_id)
    for display in the Discrepancy Explorer.
    """
    sql = f"""
        WITH run_order AS (
            SELECT DISTINCT r.run_id, r.started_at,
                   ROW_NUMBER() OVER (ORDER BY r.started_at) AS run_seq
            FROM dataguard_meta.reconciliation_runs r
            WHERE {VALID_RUN_FILTER}
        )
        SELECT
            ro.run_seq,
            ro.started_at,
            d.table_name,
            d.fault_type,
            d.dollar_impact,
            d.account_id
        FROM run_order ro
        JOIN dataguard_meta.discrepancies d ON d.run_id = ro.run_id
        ORDER BY ro.started_at DESC
    """
    return run_query(sql)