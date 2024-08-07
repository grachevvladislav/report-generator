# Generated by Django 5.0.2 on 2024-07-30 22:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_alter_schedule_time"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="schedule",
            options={
                "verbose_name": "запись",
                "verbose_name_plural": "рабочий график 📆",
            },
        ),
        migrations.AlterField(
            model_name="schedule",
            name="time",
            field=models.FloatField(
                default=None, verbose_name="Рабочее время"
            ),
        ),
    ]
