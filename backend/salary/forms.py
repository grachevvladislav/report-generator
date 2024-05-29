from django.core.exceptions import ValidationError
from django.forms import forms


class CsvForm(forms.Form):
    """CSV receive form."""

    csv_file = forms.FileField(required=True, label="Выберете файл")

    def clean_csv_file(self):
        """Validate csv_file field."""
        file = self.cleaned_data["csv_file"]
        if False:
            raise ValidationError("Email already exists")
        return file
