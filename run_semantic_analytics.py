from app.analytics.semantic_analytics import (
    matched_rules_distribution,
)
from app.analytics.semantic_analytics import (
    semantic_distribution,
)
from app.analytics.semantic_analytics import (
    unresolved_transactions,
)


print(
    "\nSemantic Distribution\n"
)

print(
    semantic_distribution()
)

print(
    "\nTop Unresolved Transactions\n"
)

print(
    unresolved_transactions()
    .head(20)
)

print(
    "\nMatched Rules Distribution\n"
)

print(
    matched_rules_distribution()
)