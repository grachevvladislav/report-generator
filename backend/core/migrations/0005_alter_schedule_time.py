# Generated by Django 5.0.2 on 2024-08-01 15:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_alter_schedule_options_alter_schedule_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schedule",
            name="time",
            field=models.FloatField(
                default=11.5, verbose_name="Рабочее время"
            ),
        ),
    ]
