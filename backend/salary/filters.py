from core.filters import EmployeeScheduleFilter

from .models import Employee


class EmployeeAccrualFilter(EmployeeScheduleFilter):
    """Group schedule by Employee."""

    role_list = [Employee.Role.TRAINER, Employee.Role.OWNER]
