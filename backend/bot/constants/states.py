import enum


class States(str, enum.Enum):
    """Bot states."""

    MAIN_MENU = "Меню"

    SCHEDULE = "Рабочий график 📆"

    WAITING_FOR_PAYMENT = "Чек готов"
    CONFIRMATION = "Подтвердить?"
