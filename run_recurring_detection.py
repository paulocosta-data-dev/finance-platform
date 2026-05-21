from app.recurring.services.recurring_detector import (
    detect_recurring_patterns,
)


patterns = (
    detect_recurring_patterns()
)

print(
    "\nRecurring Patterns\n"
)

for pattern in patterns:

    print(
        f"""
Description:
{pattern.normalized_description}

Occurrences:
{pattern.occurrences}

Average Amount:
{pattern.average_amount:.2f}

Semantic Type:
{pattern.semantic_type_id}

Category:
{pattern.category_id}

First Seen:
{pattern.first_seen}

Last Seen:
{pattern.last_seen}

Average Interval Days:
{pattern.average_interval_days:.2f}

Cadence Type:
{pattern.cadence_type}

-------------------------
"""
    )