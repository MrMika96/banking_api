# Generated by Django 4.2.7 on 2023-11-13 14:33

from django.db import migrations, models


def transfer_data(apps, schema):
    CreditCard = apps.get_model('credit_cards', 'CreditCard')
    credit_cards = CreditCard.objects.all()
    for card in credit_cards:
        card.new_balance = card.balance
        card.save(update_fields=['new_balance'])


class Migration(migrations.Migration):

    dependencies = [
        ('credit_cards', '0006_creditcard_new_balance'),
    ]

    operations = [
        migrations.RunPython(code=transfer_data),
    ]