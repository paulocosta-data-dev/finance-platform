from app.merchant.models.merchant_match import (
    MerchantMatchResult,
)

from app.merchant.services.rule_loader import (
    load_merchant_rules,
)


def detect_merchant(
    normalized_description: str,
) -> MerchantMatchResult:

    normalized_text = (
        normalized_description
        .lower()
    )

    rules = (
        load_merchant_rules()
    )

    for rule in rules:

        for keyword in (
            rule.match_contains
        ):

            if (
                keyword.lower()
                in normalized_text
            ):

                return (
                    MerchantMatchResult(
                        matched=True,
                        merchant_name=(
                            rule
                            .merchant_name
                        ),
                        confidence=0.95,
                    )
                )

    return MerchantMatchResult(
        matched=False,
        merchant_name=None,
        confidence=0.0,
    )