import datetime
import re

from django.core.exceptions import ValidationError


def exclude_future_dates(value):
    if value >= datetime.date.today():
        raise ValidationError("Введена дата из будущего!")
    return value


def passport_series_validator(value):
    reg = re.compile(r"^[0-9]{4}$")
    if not reg.match(value):
        raise ValidationError("Неверный формат. Введите 4 цифры.")


def passport_number_validator(value):
    reg = re.compile(r"^[0-9]{6}$")
    if not reg.match(value):
        raise ValidationError("Неверный формат. Введите 6 цифр.")


def phone_validater(value):
    reg = re.compile(r"^\+[0-9]{11}$")
    if not reg.match(value):
        raise ValidationError("Введите номер в формате +7XXXXXXXXXX. 11 цифр")
