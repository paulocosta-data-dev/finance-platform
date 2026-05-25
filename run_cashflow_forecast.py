from pprint import pprint

from app.cashflow.services.monthly_cashflow_service import (
    build_monthly_cashflow_summary,
)


summary = (
    build_monthly_cashflow_summary()
)

print()
print(
    "MONTHLY CASHFLOW SUMMARY"
)
print()

pprint(summary)