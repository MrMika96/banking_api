# Generated by Django 4.1.5 on 2023-02-07 06:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("credit_cards", "0004_creditcard_is_expired"),
    ]

    operations = [
        migrations.AlterField(
            model_name="creditcard",
            name="currency",
            field=models.CharField(
                choices=[
                    ("USD", "USD"),
                    ("EUR", "EUR"),
                    ("JPY", "JPY"),
                    ("RUB", "RUB"),
                    ("CNY", "CNY"),
                ],
                default=None,
                max_length=16,
                null=True,
            ),
        ),
    ]
