# Generated by Django 4.1.5 on 2023-02-07 07:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("banks", "0006_delete_currency"),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=4, unique=True)),
                ("rate", models.JSONField()),
            ],
            options={
                "db_table": "currencies",
            },
        ),
    ]
