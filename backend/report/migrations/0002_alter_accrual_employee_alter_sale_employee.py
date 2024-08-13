# Generated by Django 5.0.2 on 2024-08-12 20:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_alter_schedule_time"),
        ("report", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accrual",
            name="employee",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="accrual",
                to="core.employee",
                verbose_name="сотрудник",
            ),
        ),
        migrations.AlterField(
            model_name="sale",
            name="employee",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sale",
                to="core.employee",
                verbose_name="сотрудник",
            ),
        ),
    ]