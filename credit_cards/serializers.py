"""Module with serializers for credit card app."""
from _decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from banks.models import Bank, PaymentSystem
from credit_cards.models import CreditCard


class CreditCardSerializer(serializers.ModelSerializer):
    """Serializer for a credit card object."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bank = serializers.CharField(default="", write_only=True, required=False)
    payment_system = serializers.CharField(
        default="", write_only=True, required=False
    )
    bank_name = serializers.CharField(source="bank.name", read_only=True)
    payment_system_name = serializers.CharField(
        source="payment_system.name", read_only=True
    )

    class Meta:
        """Meta."""

        model = CreditCard
        fields = [
            "id",
            "owner",
            "number",
            "expiration_date",
            "cvv",
            "bank",
            "payment_system",
            "currency",
            "balance",
            "bank_name",
            "payment_system_name",
            "is_expired",
        ]
        read_only_fields = ["is_expired"]

    def validate_bank(self, bank):
        """Validate bank."""
        split_number = self.initial_data["number"]
        bank_number = ""
        for i in range(1, 7):
            bank_number = bank_number + split_number[i]
        if Bank.objects.filter(number=bank_number).exists():
            return Bank.objects.get(number=bank_number)
        raise ValidationError("Bank not found")

    def validate_payment_system(self, payment_system):
        """Validate payment system."""
        split_number = self.initial_data["number"]
        payment_number = split_number[0]
        if PaymentSystem.objects.filter(number=payment_number).exists():
            return PaymentSystem.objects.get(number=payment_number)
        raise ValidationError("Payment system not found")


class CreditCardCreateSerializer(serializers.ModelSerializer):
    """Serializer for credit card creation."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    expiration_date = serializers.DateField(allow_null=True, required=False)
    bank_name = serializers.CharField(source="bank.name", read_only=True)
    payment_system_name = serializers.CharField(
        source="payment_system.name", read_only=True
    )
    balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=0, required=False
    )

    class Meta:
        """Meta."""

        model = CreditCard
        fields = [
            "id",
            "owner",
            "number",
            "expiration_date",
            "cvv",
            "bank",
            "bank_name",
            "payment_system",
            "payment_system_name",
            "currency",
            "balance",
        ]
        read_only_fields = ["number", "cvv", "is_expired"]


class ChangeCardCurrencySerializer(serializers.ModelSerializer):
    """Serializer for changing credit card currency."""

    class Meta:
        """Meta."""

        model = CreditCard
        fields = ["currency"]


class CardBalanceReplenishmentSerializer(serializers.ModelSerializer):
    """Serializer for balance replenishment."""

    balance = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0),
        min_value=Decimal(0)
    )

    class Meta:
        """Meta."""

        model = CreditCard
        fields = ["balance"]


class TransferFromCardToCardSerializer(serializers.Serializer):
    """Serializer for money transferring between two cards."""

    from_card_number = serializers.CharField(
        required=True, write_only=True, max_length=19
    )
    to_card_number = serializers.CharField(
        required=True, write_only=True, max_length=19
    )
    sum_of_money = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        write_only=True,
        min_value=Decimal(0.0)
    )

    def validate_sum_of_money(self, sum_of_money):
        """Validate sum of money."""
        if sum_of_money < 0:
            raise ValidationError("Sum of money can`t be negative number")
        if (
            sum_of_money
            > CreditCard.objects.get(
                number=self.initial_data["from_card_number"],
                owner=self.context["request"].user,
            ).balance
        ):
            raise ValidationError("Insufficient funds")
        return sum_of_money
