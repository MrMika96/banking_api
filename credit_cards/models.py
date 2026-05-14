"""Module with models for credit card app."""
from decimal import Decimal
import random
import string

from django.db import models
from django.utils.translation import gettext_lazy as _
from forex_python.converter import CurrencyRates, RatesNotAvailableError

from banks.models import Currency


class CreditCard(models.Model):
    """Model of a credit card."""

    class Currency(models.TextChoices):
        """Choices of currency types."""

        USD = "USD", _("US Dollar")
        EUR = "EUR", _("Euro")
        JPY = "JPY", _("Japanese Yen")
        RUB = "RUB", _("Russian Ruble")
        CNY = "CNY", _("Chinese Yuan")

    owner = models.ForeignKey(
        "users.User", related_name="credit_cards", on_delete=models.CASCADE
    )
    number = models.CharField(max_length=19, blank=False, null=False)
    expiration_date = models.DateField(blank=False, null=False)
    is_expired = models.BooleanField(default=False)
    cvv = models.IntegerField()
    bank = models.ForeignKey(
        "banks.Bank", related_name="cards", on_delete=models.CASCADE
    )
    payment_system = models.ForeignKey(
        "banks.PaymentSystem", related_name="cards", on_delete=models.CASCADE
    )
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.RUB
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0)
    )

    class Meta:
        """Meta."""

        db_table = "credit_cards"
        unique_together = ["owner", "number"]

    @classmethod
    def cvv_generator(cls):
        """Return generated cvv."""
        return "".join(random.choices(string.digits, k=3))

    @classmethod
    def card_number_generator(cls, bank_number, payment_system_number):
        """Return generated card number."""
        existing_numbers = CreditCard.objects.values_list("number", flat=True)
        number = payment_system_number + bank_number
        while True:
            number = number + "".join(random.choices(string.digits, k=9))
            if number not in existing_numbers:
                break
        return number

    @classmethod
    def change_balance_by_currency(
        cls, old_currency: str, new_currency: str, balance: Decimal
    ) -> Decimal:
        """Return new balance after currency change."""
        if balance == 0:
            return balance
        rates = CurrencyRates()
        try:
            return rates.convert(old_currency, new_currency, balance)
        except RatesNotAvailableError:
            return Currency.convert(old_currency, new_currency, balance)
