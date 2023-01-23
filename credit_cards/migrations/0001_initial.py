# Generated by Django 4.1.5 on 2023-01-19 08:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('banks', '0003_alter_bank_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=19)),
                ('expiration_date', models.DateField()),
                ('cvv', models.IntegerField()),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='banks.bank')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_cards', to=settings.AUTH_USER_MODEL)),
                ('payment_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='banks.paymentsystem')),
            ],
            options={
                'db_table': 'credit_cards',
            },
        ),
    ]