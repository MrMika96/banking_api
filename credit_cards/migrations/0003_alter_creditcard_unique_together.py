# Generated by Django 4.1.5 on 2023-01-31 07:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("credit_cards", "0002_creditcard_balance_creditcard_currency"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="creditcard",
            unique_together={("owner", "number")},
        ),
    ]
