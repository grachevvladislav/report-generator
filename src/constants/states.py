import enum


class States(str, enum.Enum):
    """Bot states."""

    PERMISSION_DENIED = "permission_denied"

    STUFF_MENU = "stuff_menu"
    WAITING_FOR_FILE = "waiting_for_file"
    CHECK_FILE = "check_file"

    SCHEDULE = "schedule"

    WAITING_FOR_PAYMENT = "waiting_for_payment"
    CONFIRMATION = "confirmation"
