from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.forms import forms
from exceptions import ParseFail
from report.file_parse import sale_report_parsing, trainer_report_parsing


class TrainerCsvForm(forms.Form):
    """CSV receive form for trainer."""

    csv_file = forms.FileField(required=True, label="Выберете файл")

    def clean_csv_file(self):
        """Validate csv_file field."""
        file = self.cleaned_data["csv_file"]
        try:
            objects = trainer_report_parsing(file)
        except ParseFail as e:
            raise ValidationError(e)
        return objects


class SaleCsvForm(forms.Form):
    """CSV receive form for sale."""

    csv_file = forms.FileField(required=True, label="Выберете файл")

    def clean_csv_file(self):
        """Validate csv_file field."""
        file = self.cleaned_data["csv_file"]
        try:
            objects = sale_report_parsing(file)
        except (ParseFail, IntegrityError) as e:
            raise ValidationError(e)

        return objects
