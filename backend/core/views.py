from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse

from .crud import export_all_tables


def make_backup(request):
    """Download backup file function."""
    messages.success(request, "Загрузка начата!")
    file = export_all_tables()
    response = HttpResponse(file, content_type="application/json")
    response["Content-Disposition"] = (
        "attachment; filename=data_"
        + datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
        + ".json"
    )
    return response
