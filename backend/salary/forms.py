from django.core.exceptions import ValidationError
from django.forms import forms

from .exceptions import ParseFail
from .file_parse import sale_report_parsing, trainer_report_parsing


class TrainerCsvForm(forms.Form):
    """CSV receive form for trainer."""

    csv_file = forms.FileField(required=True, label="Выберете файл")
    parser = trainer_report_parsing

    def clean_csv_file(self):
        """Validate csv_file field."""
        file = self.cleaned_data["csv_file"]
        try:
            objects = self.parser(file)
        except ParseFail as e:
            raise ValidationError(e)
        return objects


class SaleCsvForm(TrainerCsvForm):
    """CSV receive form for sale."""

    parser = sale_report_parsing
