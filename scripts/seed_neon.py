"""
One-time script: copies dataguard_meta's schema and a small,
real subset of data from the local dev Postgres to Neon, so the
public Streamlit deployment has genuine (not fake) data to show,
without ever pointing the live app at the local dev database.
"""
import psycopg2

LOCAL_DSN = "postgresql://dataguard:dataguard_dev_pw@localhost:55432/dataguard"
NEON_DSN = "postgresql://neondb_owner:npg_qClTX5vEJ7FQ@ep-odd-credit-aegobnge-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS dataguard_meta;

CREATE TABLE IF NOT EXISTS dataguard_meta.reconciliation_runs (
    run_id SERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_seconds NUMERIC,
    total_rows_checked BIGINT,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dataguard_meta.discrepancies (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES dataguard_meta.reconciliation_runs(run_id),
    table_name TEXT,
    row_pk BIGINT,
    field TEXT,
    fault_type TEXT,
    dollar_impact NUMERIC,
    account_id BIGINT
);
"""


def main():
    local_conn = psycopg2.connect(LOCAL_DSN)
    neon_conn = psycopg2.connect(NEON_DSN)

    local_cur = local_conn.cursor()
    neon_cur = neon_conn.cursor()

    print("Creating schema on Neon...")
    neon_cur.execute(SCHEMA_SQL)
    neon_conn.commit()

    print("Clearing any existing seed data on Neon...")
    neon_cur.execute("TRUNCATE dataguard_meta.discrepancies, dataguard_meta.reconciliation_runs CASCADE;")
    neon_conn.commit()

    print("Copying reconciliation_runs...")
    local_cur.execute("""
        SELECT run_id, started_at, finished_at, duration_seconds, total_rows_checked, status
        FROM dataguard_meta.reconciliation_runs
        WHERE total_rows_checked IS NOT NULL
        ORDER BY started_at
    """)
    runs = local_cur.fetchall()
    for run in runs:
        neon_cur.execute("""
            INSERT INTO dataguard_meta.reconciliation_runs
            (run_id, started_at, finished_at, duration_seconds, total_rows_checked, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, run)
    neon_conn.commit()
    print(f"Copied {len(runs)} runs.")

    print("Copying discrepancies for those runs...")
    run_ids = [r[0] for r in runs]
    local_cur.execute("""
        SELECT run_id, table_name, row_pk, field, fault_type, dollar_impact, account_id
        FROM dataguard_meta.discrepancies
        WHERE run_id = ANY(%s)
    """, (run_ids,))
    discrepancies = local_cur.fetchall()
    for d in discrepancies:
        neon_cur.execute("""
            INSERT INTO dataguard_meta.discrepancies
            (run_id, table_name, row_pk, field, fault_type, dollar_impact, account_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, d)
    neon_conn.commit()
    print(f"Copied {len(discrepancies)} discrepancies.")

    # Fix the sequences so future inserts (if any) don't collide with copied IDs
    neon_cur.execute("SELECT setval('dataguard_meta.reconciliation_runs_run_id_seq', (SELECT MAX(run_id) FROM dataguard_meta.reconciliation_runs));")
    neon_cur.execute("SELECT setval('dataguard_meta.discrepancies_id_seq', (SELECT MAX(id) FROM dataguard_meta.discrepancies));")
    neon_conn.commit()

    local_cur.close()
    neon_cur.close()
    local_conn.close()
    neon_conn.close()
    print("Done.")


if __name__ == "__main__":
    main()