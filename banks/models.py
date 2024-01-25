from django.db import models
from django.shortcuts import get_object_or_404


class Bank(models.Model):
    BANK_TYPE = [
        ("central bank", "central bank"),
        ("commercial bank", "commercial bank"),
        ("investment bank", "investment bank"),
        ("savings bank", "savings bank"),
        ("mortgage bank", "mortgage bank"),
        ("special bank", "special bank"),
    ]
    name = models.CharField(max_length=128, blank=False, null=False, unique=True)
    type = models.CharField(max_length=16, choices=BANK_TYPE, blank=False, null=False)
    number = models.CharField(max_length=6, blank=False, null=False)

    class Meta:
        db_table = "banks"


class PaymentSystem(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False, unique=True)
    number = models.CharField(max_length=2, blank=False, null=False, unique=True)

    class Meta:
        db_table = "payment_systems"


class Currency(models.Model):
    name = models.CharField(max_length=4, blank=False, null=False, unique=True)
    rates = models.JSONField()

    class Meta:
        db_table = "currencies"

    @classmethod
    def convert(cls, old_currency, new_currency, balance):
        convert_to_currency = get_object_or_404(Currency, name=old_currency)
        return convert_to_currency.rates[new_currency] * balance
