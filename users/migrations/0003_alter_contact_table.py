# Generated by Django 4.1.5 on 2023-01-19 11:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_contact"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="contact",
            table="contacts",
        ),
    ]
