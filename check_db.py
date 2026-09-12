from app.db import run_query

df = run_query("SELECT run_id, started_at, duration_seconds, status FROM dataguard_meta.reconciliation_runs ORDER BY run_id;")
print(df)
print(f"\nShape: {df.shape}")