import enum


class States(str, enum.Enum):
    """Bot states."""

    WAITING_FOR_FILE = "waiting_for_file"
    PERMISSION_DENIED = "permission_denied"
    CHECK_FILE = "check_file"
