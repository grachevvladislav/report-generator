from datetime import datetime

from constants.exceptions import InnerFail
from utils import key_name_generator


class Employee:
    """Employee class."""

    def __init__(
        self,
        fio: str = "",
        tax: str = "",
        inn: str = "",
        ogrnip: str = "",
        address: str = "",
        checking_account: str = "",
        bank: str = "",
        bik: str = "",
        correspondent_account: str = "",
        agreement_number: str = "",
        agreement_date: str = "",
        telegram_id: str = "",
        role: str = "",
        admin_work_time: float = 0,
        admin_money: float = 0,
        conducted_classes: dict = {},
        is_for_report: bool = False,
    ):
        """Init method."""
        self.fio: str = fio
        self.tax: str = tax
        self.inn: str = inn
        self.ogrnip: str = ogrnip
        self.address: str = address
        self.checking_account: str = checking_account
        self.bank: str = bank
        self.bik: str = bik
        self.correspondent_account: str = correspondent_account
        self.agreement_number: str = agreement_number
        self.agreement_date: str = agreement_date
        self.telegram_id: str = telegram_id
        self.role: str = role
        self.admin_work_time: float = admin_work_time
        self.admin_money: float = admin_money
        self.conducted_classes: dict = conducted_classes
        self.is_for_report: bool = is_for_report

    def to_dict(self):
        """Get dict of object property."""
        return vars(self)


class Employees:
    """Set of employees."""

    def __init__(self):
        """Init method."""
        self.dict: dict = {}
        self.notification: list = []

    def get_names(self):
        """List of key name all employees."""
        return self.dict.keys()

    def add_notification(self, comment):
        """Append item to set."""
        self.notification.append(comment)

    def get_active_employee(self) -> list:
        """Gey list of employees with full data."""
        active = []
        for employee in self.dict.values():
            if employee.is_for_report:
                active.append(employee)
        return active

    def add_employee(self, *_, **kwargs) -> None:
        """Add new employee."""
        if not kwargs["fio"]:
            raise InnerFail(
                "Нельзя добавить сотрудника без имени.\n"
                + " ".join(kwargs.values())
            )
        key_name = key_name_generator(kwargs["fio"])
        if key_name in self.dict.keys():
            raise InnerFail(
                f"Добавление нового сотрудника.\n"
                f"Сотрудник {kwargs['fio']} уже существует."
            )
        else:
            self.dict[key_name] = Employee(**kwargs)

    def set_attribute(self, name, *_, **kwargs):
        """Set params to employee."""
        name = kwargs.pop("fio", name)
        key_name = key_name_generator(name)
        if key_name not in self.dict.keys():
            self.add_employee(fio=name, **kwargs)
        else:
            for key, new_value in kwargs.items():
                old_value = getattr(self.dict[key_name], key)
                if isinstance(old_value, float):
                    if not isinstance(new_value, float):
                        raise InnerFail(
                            f"Нельзя складывать разные типы данных: \n"
                            f"{old_value} + {new_value}"
                        )
                    new_value += old_value
                elif isinstance(old_value, dict):
                    if not isinstance(new_value, dict):
                        raise InnerFail(
                            f"Нельзя складывать разные типы данных: \n"
                            f"{old_value} + {new_value}"
                        )
                    for dict_key, dict_value in old_value.items():
                        if dict_key in new_value.keys():
                            try:
                                new_value[dict_key] += dict_value
                            except TypeError:
                                raise InnerFail(
                                    f"Нельзя складывать разные типы данных: \n"
                                    f"{dict_value} + {new_value[dict_key]}"
                                )
                        else:
                            new_value[dict_key] = dict_value
                setattr(self.dict[key_name], key, new_value)


class WorkingDay:
    """Admins working day."""

    def __init__(self, date=None, fio=None, delimiter=False):
        """Init method."""
        self.date: datetime = date
        self.fio: str = fio
        self.delimiter: bool = delimiter

    def _complete_symbol(self, date: datetime) -> str:
        if date > self.date:
            return "✅"
        else:
            return "☑️"

    def full_string(self, date: datetime, full: bool = True) -> str:
        """Return all info in string."""
        if self.delimiter:
            return "----\n"
        elif full:
            return " ".join(
                [
                    self._complete_symbol(date),
                    self.date.strftime("%d %B"),
                    key_name_generator(self.fio),
                    "\n",
                ]
            )
        else:
            return " ".join(
                [
                    self._complete_symbol(date),
                    self.date.strftime("%d %B"),
                    "\n",
                ]
            )
