from django.contrib import admin
from django.urls import path

admin.site.site_header = "CRM Легкость"
admin.site.index_title = "Студия йоги для женщин"


urlpatterns = [
    path("", admin.site.urls),
]
