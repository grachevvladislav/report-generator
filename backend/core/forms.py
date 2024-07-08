from django import forms
from utils import get_current_month, get_current_year, get_years_range

from constants import months_int


class DateRangeForm(forms.Form):
    """CSV receive form for trainer."""

    month = forms.ChoiceField(
        label="Месяц", choices=months_int, initial=get_current_month
    )
    year = forms.ChoiceField(
        label="Год", choices=get_years_range, initial=get_current_year
    )
