from datetime import datetime

from app.domain.categories import Category


CATEGORIES = [
    Category(
        category_id="groceries",
        name="Groceries",
        created_at=datetime.now(),
    ),
    Category(
        category_id="restaurants",
        name="Restaurants",
        created_at=datetime.now(),
    ),
    Category(
        category_id="transport",
        name="Transport",
        created_at=datetime.now(),
    ),
    Category(
        category_id="housing",
        name="Housing",
        created_at=datetime.now(),
    ),
    Category(
        category_id="shopping",
        name="Shopping",
        created_at=datetime.now(),
    ),
    Category(
        category_id="health",
        name="Health",
        created_at=datetime.now(),
    ),
    Category(
        category_id="salary",
        name="Salary",
        created_at=datetime.now(),
    ),
    Category(
        category_id="bank_fees",
        name="Bank Fees",
        created_at=datetime.now(),
    ),
]