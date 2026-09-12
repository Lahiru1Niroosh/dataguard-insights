from app.queries.trends import get_run_history, get_rolling_integrity, get_month_over_month_impact, get_fault_type_distribution
from app.queries.risk import get_top_accounts_by_impact

print("=== Run History ===")
print(get_run_history())

print("\n=== Rolling Integrity ===")
print(get_rolling_integrity())

print("\n=== Month-over-Month Impact ===")
print(get_month_over_month_impact())

print("\n=== Fault Type Distribution ===")
print(get_fault_type_distribution())

print("\n=== Top Accounts by Impact ===")
print(get_top_accounts_by_impact(top_n=5))