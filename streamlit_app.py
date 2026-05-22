import streamlit as st

from app.ui.services.category_service import (
    load_available_categories,
)

from app.ui.services.review_service import (
    save_corrections,
)

from app.ui.services.transaction_service import (
    apply_session_overrides,
    load_unresolved_transactions,
)


AVAILABLE_CATEGORIES = (
    load_available_categories()
)


st.set_page_config(
    page_title="Finance Platform",
    layout="wide",
)

st.title(
    "Finance Platform"
)

st.subheader(
    "Unresolved Transactions Review"
)

if (
    "available_categories"
    not in st.session_state
):

    st.session_state[
        "available_categories"
    ] = (
        AVAILABLE_CATEGORIES.copy()
    )

if (
    "pending_corrections"
    not in st.session_state
):

    st.session_state[
        "pending_corrections"
    ] = {}

unresolved_df = (
    load_unresolved_transactions()
)

unresolved_df = (
    apply_session_overrides(
        unresolved_df,
        st.session_state[
            "pending_corrections"
        ],
    )
)

unresolved_count = len(
    unresolved_df
)

st.warning(
    f"""
There are currently
{unresolved_count}
unresolved transactions.
"""
)

if unresolved_df.empty:

    st.success(
        """
All transactions
have been reviewed.
"""
    )

    st.stop()

st.divider()

header_cols = st.columns(
    [1.2, 4, 1.2, 1.5, 2, 2, 1.5]
)

headers = [
    "Date",
    "Description",
    "Amount",
    "Suggested",
    "Select Category",
    "New Category",
    "Apply All",
]

for col, header in zip(
    header_cols,
    headers,
):

    col.markdown(
        f"""
**{header}**
"""
    )

st.divider()

for index, row in unresolved_df.iterrows():

    transaction_id = row[
        "transaction_id"
    ]

    cols = st.columns(
        [1.2, 4, 1.2, 1.5, 2, 2, 1.5]
    )

    cols[0].write(
        str(
            row[
                "transaction_date"
            ]
        )[:10]
    )

    cols[1].write(
        row[
            "description"
        ]
    )

    cols[2].write(
        round(
            row["amount"],
            2,
        )
    )

    cols[3].write(
        row[
            "category_id"
        ]
    )

    selected_category = (
        cols[4].selectbox(
            label="Category",
            options=(
                st.session_state[
                    "available_categories"
                ]
            ),
            index=(
                st.session_state[
                    "available_categories"
                ].index(
                    row[
                        "category_id"
                    ]
                )
                if row[
                    "category_id"
                ]
                in st.session_state[
                    "available_categories"
                ]
                else 0
            ),
            label_visibility="collapsed",
            key=(
                f"""
    select_
    {transaction_id}
    """
            ),
        )
    )

    new_category = (
        cols[5].text_input(
            label="New Category",
            placeholder=(
                "Create..."
            ),
            label_visibility="collapsed",
            key=(
                f"""
new_category_
{transaction_id}
"""
            ),
        )
    )

    apply_to_all = (
        cols[6].checkbox(
            label="Apply All",
            key=(
                f"""
apply_all_
{transaction_id}
"""
            ),
        )
    )

    if (
        new_category
        and new_category
        not in st.session_state[
            "available_categories"
        ]
    ):

        st.session_state[
            "available_categories"
        ].append(
            new_category
        )

        selected_category = (
            new_category
        )

if (
    selected_category
    != row["category_id"]
    or apply_to_all
):

    st.session_state[
        "pending_corrections"
    ][transaction_id] = {
        "category_id": (
            selected_category
        ),
        "apply_to_all": (
            apply_to_all
        ),
        "description": (
            row[
                "description"
            ]
        ),
    }

st.divider()

st.info(
    f"""
Pending corrections:
{len(st.session_state['pending_corrections'])}
"""
)

if st.button(
    "Apply Changes"
):

    save_corrections(
        corrections=(
            st.session_state[
                "pending_corrections"
            ]
        ),
        unresolved_df=(
            unresolved_df
        ),
    )

    st.success(
        """
Corrections applied successfully.

Changes applied successfully.
"""
    )

    st.session_state[
        "pending_corrections"
    ] = {}

    st.rerun()