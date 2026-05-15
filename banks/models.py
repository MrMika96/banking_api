"""Module with models for bank app."""
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


class Bank(models.Model):
    """Model for bank."""

    class BankTypes(models.TextChoices):
        """Choices of bank types."""

        CENTRAL = "cnt", _("Central Bank")
        COMMERCIAL = "com", _("Commercial Bank")
        INVESTMENT = "inv", _("Investment Bank")
        SAVINGS = "sav", _("Savings Bank")
        MORTGAGE = "mrg", _("Mortgage Bank")
        SPECIAL = "spc", _("Special Bank")

    name = models.CharField(
        max_length=128,
        blank=False,
        null=False,
        unique=True
    )
    bank_type = models.CharField(
        max_length=16,
        choices=BankTypes.choices,
        default=BankTypes.COMMERCIAL
    )
    number = models.CharField(max_length=6, blank=False, null=False)

    class Meta:
        """Meta."""

        db_table = "banks"


class PaymentSystem(models.Model):
    """Model for payment system of banks."""

    name = models.CharField(
        max_length=128,
        blank=False,
        null=False,
        unique=True
    )
    number = models.CharField(
        max_length=2,
        blank=False,
        null=False,
        unique=True
    )

    class Meta:
        """Meta."""

        db_table = "payment_systems"


class Currency(models.Model):
    """Model for currency."""

    name = models.CharField(max_length=4, blank=False, null=False, unique=True)
    rates = models.JSONField()

    class Meta:
        """Meta."""

        db_table = "currencies"

    @classmethod
    def convert(
        cls,
        old_currency: str,
        new_currency: str,
        balance: Decimal
    ) -> Decimal:
        """Return converted balance."""
        convert_to_currency = get_object_or_404(Currency, name=old_currency)
        result = Decimal(
            str(convert_to_currency.rates[new_currency])
        ) * balance
        return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
