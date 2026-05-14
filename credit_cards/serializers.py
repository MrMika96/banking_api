"""Module with serializers for credit card app."""
from _decimal import Decimal
import datetime

from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
    bank = serializers.PrimaryKeyRelatedField(
        queryset=Bank.objects.all(), write_only=True
    )
    payment_system = serializers.PrimaryKeyRelatedField(
        queryset=PaymentSystem.objects.all(), write_only=True
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

    def create(self, validated_data):
        """Create credit card."""
        validated_data["number"] = CreditCard.card_number_generator(
            validated_data["bank"].number,
            validated_data["payment_system"].number
        )
        validated_data["cvv"] = CreditCard.cvv_generator()
        validated_data["expiration_date"] = (
                timezone.now().date() + datetime.timedelta(days=1825)
        )
        return CreditCard.objects.create(**validated_data)


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

    def validate_balance(self, balance):
        """Validate balance."""
        if balance < 0:
            raise ValidationError("Balance can`t be negative number")
        return balance

    def update(self, instance, validated_data):
        """Update balance of a credit card."""
        instance.balance = instance.balance + validated_data["balance"]
        instance.full_clean()
        instance.save(update_fields=["balance"])
        return instance


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

    def validate_from_card_number(self, from_card_number):
        """Validate credit giving credit card number."""
        if not CreditCard.objects.filter(
            number=from_card_number, owner=self.context["request"].user
        ).exists():
            raise ValidationError(detail="Card with this number is not found")
        return from_card_number

    def validate_to_card_number(self, to_card_number):
        """Validate credit receiving credit card number."""
        if not CreditCard.objects.filter(number=to_card_number).exists():
            raise ValidationError(detail="Card with this number is not found")
        return to_card_number

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

    def to_representation(self, instance):
        """Return simple message instead of an object."""
        return {"status": "Complete!"}

    @atomic
    def create(self, validated_data):
        """Transfer money from one card to another."""
        to_card = get_object_or_404(
            CreditCard, number=validated_data["to_card_number"]
        )
        from_card = get_object_or_404(
            CreditCard, number=validated_data["from_card_number"]
        )
        from_card.balance = from_card.balance - validated_data["sum_of_money"]
        from_card.full_clean()
        from_card.save(update_fields=["balance"])
        if to_card.currency != from_card.currency:
            to_card.balance = (
                    to_card.balance +
                    CreditCard.change_balance_by_currency(
                        from_card.currency,
                        to_card.currency,
                        validated_data["sum_of_money"]
                    )
            )
        else:
            to_card.balance = to_card.balance + validated_data["sum_of_money"]
        to_card.full_clean()
        to_card.save(update_fields=["balance"])
        return to_card
