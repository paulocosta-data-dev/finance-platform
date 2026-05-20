from enum import Enum


class DirectionEnum(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class ResolutionStatusEnum(str, Enum):
    AUTO_RESOLVED = "AUTO_RESOLVED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    MANUALLY_RESOLVED = "MANUALLY_RESOLVED"
    ALLOCATED = "ALLOCATED"


class AccountTypeEnum(str, Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    CREDIT_CARD = "CREDIT_CARD"
    CASH = "CASH"
    INVESTMENT = "INVESTMENT"