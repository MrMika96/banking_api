# Generated by Django 4.1.5 on 2023-01-31 07:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("banks", "0003_alter_bank_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bank",
            name="name",
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name="paymentsystem",
            name="name",
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name="paymentsystem",
            name="number",
            field=models.CharField(max_length=2, unique=True),
        ),
    ]
