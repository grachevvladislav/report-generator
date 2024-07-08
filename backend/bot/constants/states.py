import enum


class States(str, enum.Enum):
    """Bot states."""

    PERMISSION_DENIED = "permission_denied"

    SCHEDULE = "schedule"

    WAITING_FOR_PAYMENT = "waiting_for_payment"
    CONFIRMATION = "confirmation"
