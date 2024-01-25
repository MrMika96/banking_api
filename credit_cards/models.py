import random
import string

from django.db import models
from forex_python.converter import CurrencyRates, RatesNotAvailableError

from banks.models import Currency
from users.models import User


class CreditCard(models.Model):
    CURRENCY_CHOICES = [
        ("USD", "USD"),
        ("EUR", "EUR"),
        ("JPY", "JPY"),
        ("RUB", "RUB"),
        ("CNY", "CNY"),
    ]
    owner = models.ForeignKey(
        User, related_name="credit_cards", on_delete=models.CASCADE
    )
    number = models.CharField(max_length=19, blank=False, null=False)
    expiration_date = models.DateField(blank=False, null=False)
    is_expired = models.BooleanField(default=False)
    cvv = models.IntegerField()
    bank = models.ForeignKey("Bank", related_name="cards", on_delete=models.CASCADE)
    payment_system = models.ForeignKey(
        "PaymentSystem", related_name="cards", on_delete=models.CASCADE
    )
    currency = models.CharField(
        max_length=16, choices=CURRENCY_CHOICES, null=True, default=None
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "credit_cards"
        unique_together = ["owner", "number"]

    @classmethod
    def cvv_generator(cls):
        return "".join(random.choices(string.digits, k=3))

    @classmethod
    def card_number_generator(cls, bank_number, payment_system_number):
        existing_numbers = CreditCard.objects.values_list("number", flat=True)
        number = payment_system_number + bank_number
        while True:
            number = number + "".join(random.choices(string.digits, k=9))
            if number not in existing_numbers:
                break
        return number

    @classmethod
    def change_balance_by_currency(
        cls, old_currency: str, new_currency: str, balance: float
    ):
        if balance == 0:
            return balance
        else:
            rates = CurrencyRates()
            try:
                return rates.convert(old_currency, new_currency, balance)
            except RatesNotAvailableError:
                return Currency.convert(old_currency, new_currency, balance)
