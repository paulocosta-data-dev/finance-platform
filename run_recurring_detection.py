from pprint import pprint

from app.category.services.recurring_detection_service import (
    detect_recurring_transactions,
)


results = (
    detect_recurring_transactions()
)

print()

print(
    "DETECTED RECURRING TRANSACTIONS"
)

print()

print(
    f"TOTAL DETECTED: {len(results)}"
)

print()

pprint(results)