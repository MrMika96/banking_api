"""Unit tests for credit cards repository module."""
from collections import OrderedDict
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from banks.models import Bank, PaymentSystem
from users.repositories.user_repositories import UserRepository
from ..repositories.credit_card_repositories import CreditCardRepository


class BaseCreditCardUnitTestCase(TestCase):
    """Base test case for credit card unit tests."""

    def setUp(self):
        """Set up common test environment."""
        super().setUp()
        call_command(
            "loaddata",
            "banks/fixtures/initial_data.json",
            verbosity=0
        )
        self.repository = CreditCardRepository()
        user_data = OrderedDict(
            {
                "email": "test@test.com",
                "password": "test123456",
                "profile": {
                    "first_name": "Test",
                    "middle_name": "Testovich",
                    "last_name": "Testov",
                    "phone": "+79990008877",
                    "birth_date": "1990-01-01",
                },
            }
        )
        self.user = UserRepository().register_user(user_data)
        self.bank = Bank.objects.first()
        self.payment_system = PaymentSystem.objects.first()


class CreditCardRepositoryCreateTest(BaseCreditCardUnitTestCase):
    """Tests for create_credit_card method."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.valid_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
                "balance": Decimal(1000.00),
            }
        )

    def test_create_credit_card_success(self):
        """Test successful credit card creation."""
        card = self.repository.create_credit_card(self.valid_data)

        self.assertIsNotNone(card.pk)
        self.assertEqual(card.owner, self.user)
        self.assertEqual(card.bank, self.bank)
        self.assertEqual(card.payment_system, self.payment_system)
        self.assertEqual(card.balance, Decimal(1000.00))
        self.assertEqual(card.currency, "USD")
        self.assertEqual(
            card.expiration_date, timezone.now().date() + timedelta(days=1825)
        )
        self.assertTrue(len(card.number) >= 16)
        self.assertTrue(len(str(card.cvv)) == 3)

    def test_create_credit_card_with_zero_balance(self):
        """Test creating credit card with zero balance."""
        self.valid_data["balance"] = Decimal(0.00)
        card = self.repository.create_credit_card(self.valid_data)

        self.assertEqual(card.balance, Decimal(0.00))


class CreditCardRepositoryUpdateCurrencyTest(BaseCreditCardUnitTestCase):
    """Tests for update_credit_card_currency method."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.card_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
                "balance": Decimal(1000.00),
            }
        )
        self.card = self.repository.create_credit_card(self.card_data)

    def test_update_currency_success(self):
        """Test successful currency update."""
        new_currency_data = OrderedDict({"currency": "EUR"})

        with patch("credit_cards.models.CurrencyRates") as mock_rates:
            mock_rates.return_value.convert.return_value = Decimal(850.50)
            updated_card = self.repository.update_credit_card_currency(
                self.card, new_currency_data
            )

        self.assertEqual(updated_card.currency, "EUR")
        self.assertEqual(updated_card.balance, Decimal(850.50))

    def test_update_currency_same_currency(self):
        """Test updating currency to the same value."""
        new_currency_data = OrderedDict({"currency": "USD"})
        updated_card = self.repository.update_credit_card_currency(
            self.card, new_currency_data
        )
        self.assertEqual(updated_card.currency, "USD")
        self.assertEqual(updated_card.balance, Decimal(1000.00))

    def test_update_currency_zero_balance(self):
        """Test updating currency when balance is zero."""
        self.card.balance = Decimal(0.00)
        self.card.save()
        new_currency_data = OrderedDict({"currency": "EUR"})
        updated_card = self.repository.update_credit_card_currency(
            self.card, new_currency_data
        )
        self.assertEqual(updated_card.currency, "EUR")
        self.assertEqual(updated_card.balance, Decimal(0.00))


class CreditCardRepositoryReplenishTest(BaseCreditCardUnitTestCase):
    """Tests for replenish_credit_card_balance method."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.card_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
                "balance": Decimal(1000.00),
            }
        )
        self.card = self.repository.create_credit_card(self.card_data)

    def test_replenish_balance_success(self):
        """Test successful balance replenishment."""
        replenish_data = OrderedDict({"balance": Decimal(500.00)})
        updated_card = self.repository.replenish_credit_card_balance(
            self.card, replenish_data
        )
        self.assertEqual(updated_card.balance, Decimal(1500.00))

    def test_replenish_balance_with_zero(self):
        """Test replenishing with zero amount."""
        replenish_data = OrderedDict({"balance": Decimal(0.00)})
        updated_card = self.repository.replenish_credit_card_balance(
            self.card, replenish_data
        )
        self.assertEqual(updated_card.balance, Decimal(1000.00))


class CreditCardRepositoryRetrieveTest(BaseCreditCardUnitTestCase):
    """Tests for get_credit_card methods."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.card_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
                "balance": Decimal(1000.00),
            }
        )
        self.card = self.repository.create_credit_card(self.card_data)

    def test_get_credit_card_by_number_success(self):
        """Test retrieving card by number."""
        found_card = self.repository.get_credit_card_by_number(
            self.card.number
        )
        self.assertEqual(found_card.pk, self.card.pk)
        self.assertEqual(found_card.number, self.card.number)

    def test_get_credit_card_by_pk_success(self):
        """Test retrieving card by primary key."""
        found_card = self.repository.get_credit_card_by_pk(self.card.pk)
        self.assertEqual(found_card.pk, self.card.pk)

    def test_get_credit_card_by_number_not_found(self):
        """Test retrieving non-existent card by number."""
        with self.assertRaises(Exception):
            self.repository.get_credit_card_by_number("1234567890123456")


class CreditCardRepositoryTransferTest(BaseCreditCardUnitTestCase):
    """Tests for transfer_money_from_one_card_to_another method."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.from_card_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
                "balance": Decimal(1000.00),
            }
        )
        self.to_card_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
                "balance": Decimal(500.00),
            }
        )
        self.from_card = self.repository.create_credit_card(
            self.from_card_data
        )
        self.to_card = self.repository.create_credit_card(self.to_card_data)

    def test_transfer_same_currency_success(self):
        """Test successful transfer between cards with same currency."""
        operation_data = OrderedDict({"sum_of_money": Decimal(300.00)})
        self.repository.transfer_money_from_one_card_to_another(
            self.to_card, self.from_card, operation_data
        )
        self.from_card.refresh_from_db()
        self.to_card.refresh_from_db()
        self.assertEqual(self.from_card.balance, Decimal(700.00))
        self.assertEqual(self.to_card.balance, Decimal(800.00))

    def test_transfer_insufficient_funds(self):
        """Test transfer when sender has insufficient funds."""
        operation_data = OrderedDict({"sum_of_money": Decimal("1500")})
        self.repository.transfer_money_from_one_card_to_another(
            self.to_card, self.from_card, operation_data
        )
        self.from_card.refresh_from_db()
        self.to_card.refresh_from_db()
        self.assertEqual(self.from_card.balance, Decimal("-500"))
        self.assertEqual(self.to_card.balance, Decimal("2000"))

    def test_transfer_different_currency_with_conversion(self):
        """Test transfer between cards with different currencies."""
        self.to_card.currency = "EUR"
        self.to_card.save()
        operation_data = OrderedDict({"sum_of_money": Decimal(100.00)})
        with patch("credit_cards.models.CurrencyRates") as mock_rates:
            mock_rates.return_value.convert.return_value = Decimal(85.50)
            self.repository.transfer_money_from_one_card_to_another(
                self.to_card, self.from_card, operation_data
            )
        self.from_card.refresh_from_db()
        self.to_card.refresh_from_db()
        self.assertEqual(self.from_card.balance, Decimal(900.00))
        self.assertEqual(self.to_card.balance, Decimal(585.50))

    def test_transfer_zero_amount(self):
        """Test transferring zero amount."""
        operation_data = OrderedDict({"sum_of_money": Decimal(0.00)})
        self.repository.transfer_money_from_one_card_to_another(
            self.to_card, self.from_card, operation_data
        )
        self.from_card.refresh_from_db()
        self.to_card.refresh_from_db()
        self.assertEqual(self.from_card.balance, Decimal(1000.00))
        self.assertEqual(self.to_card.balance, Decimal(500.00))


class CreditCardRepositoryEdgeCasesTest(BaseCreditCardUnitTestCase):
    """Tests for edge cases in credit card repository."""

    def test_create_multiple_cards_unique_numbers(self):
        """Test creating multiple cards generates unique numbers."""
        card1_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
                "balance": Decimal(1000.00),
            }
        )
        card2_data = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "EUR",
                "balance": Decimal(500.00),
            }
        )
        card1 = self.repository.create_credit_card(card1_data)
        card2 = self.repository.create_credit_card(card2_data)
        self.assertNotEqual(card1.number, card2.number)

    def test_create_credit_card_without_balance(self):
        """Test creating credit card without specifying balance."""
        data_without_balance = OrderedDict(
            {
                "owner": self.user,
                "bank": self.bank,
                "payment_system": self.payment_system,
                "currency": "USD",
            }
        )
        card = self.repository.create_credit_card(data_without_balance)
        self.assertEqual(card.balance, Decimal(0.00))
