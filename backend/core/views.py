from django.shortcuts import render

from .models import Employee


def employee_list(request):
    employees = Employee.objects.order_by("agreement_number")
    context = {
        "employees": employees,
    }
    return render(request, "employee_list.html", context)
