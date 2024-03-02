from django.urls import path

from . import views

urlpatterns = [
    path("", views.employee_list, name="add_employee"),
]
