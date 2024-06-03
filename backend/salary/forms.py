from django.core.exceptions import ValidationError
from django.forms import forms

from .exceptions import ParseFail
from .file_parse import report_parsing


class CsvForm(forms.Form):
    """CSV receive form."""

    csv_file = forms.FileField(required=True, label="Выберете файл")

    def clean_csv_file(self):
        """Validate csv_file field."""
        file = self.cleaned_data["csv_file"]
        try:
            objects = report_parsing(file)
        except ParseFail as e:
            raise ValidationError(e)
        return objects
