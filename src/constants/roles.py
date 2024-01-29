import enum


class Roles(str, enum.Enum):
    """EmployeesRole."""

    ADMINISTRATOR = "Администратор"
    TRAINER = "Тренер"
