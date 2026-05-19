"""Module for e2e testing for credit cards app."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from credit_cards.models import CreditCard

User = get_user_model()


class BaseCreditCardTenantTestCase(TenantTestCase):
    """Parent class for all tests."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()

        self.tenant.save()
        self.domain.save()
        self.c = TenantClient(self.tenant)
        call_command(
            "loaddata",
            "banks/fixtures/initial_data.json",
            verbosity=0
        )
        self.test_user_data = {
            "email": "user@test.com",
            "password": "test123456",
            "profile": {
                "first_name": "Test",
                "middle_name": "Test",
                "last_name": "Test",
                "phone": "+79990008877",
                "birth_date": timezone.now().date(),
            },
        }
        self.user = User.objects.register(**self.test_user_data)
        self.credit_card_1 = {
            "balance": Decimal("255.96"),
            "bank_id": 3,
            "currency": "EUR",
            "cvv": 556,
            "expiration_date": date(2031, 5, 14),
            "is_expired": False,
            "number": "2223344404934911",
            "owner_id": self.user.id,
            "payment_system_id": 2,
        }
        self.credit_card_2 = {
            "balance": Decimal("10000.00"),
            "bank_id": 4,
            "currency": "EUR",
            "cvv": 381,
            "expiration_date": date(2031, 5, 14),
            "is_expired": False,
            "number": "3334455106542903",
            "owner_id": self.user.id,
            "payment_system_id": 3,
        }
        for card in [self.credit_card_1, self.credit_card_2]:
            CreditCard.objects.create(**card)


class TestCreditCards(BaseCreditCardTenantTestCase):
    """Tests for credit cards."""

    def test_get_all_users_credit_cards(self):
        """Testing geting full list of users credit cards."""
        self.c.force_login(self.user)
        url = reverse("credit-card-list")
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), self.user.credit_cards.count())

    def test_get_credit_card_by_id(self):
        """Testing getting credit card by it`s id."""
        self.c.force_login(self.user)
        credit_card = self.user.credit_cards.first()
        url = reverse("credit-card-detail", kwargs={"pk": credit_card.id})
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["number"], credit_card.number)

    def test_update_credit_card_data(self):
        """Test partial update functionality for credit cards."""
        self.c.force_login(self.user)
        credit_card = self.user.credit_cards.first()
        new_credit_card_data = {
            "expiration_date": date(2026, 5, 19),
            "bank": 1,
            "payment_system": 1,
            "currency": "USD",
        }
        url = reverse("credit-card-detail", kwargs={"pk": credit_card.id})
        response = self.c.patch(
            url,
            data=new_credit_card_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        credit_card.refresh_from_db()
        for key in new_credit_card_data:
            match key:
                case "expiration_date":
                    self.assertEqual(
                        response.data[key],
                        str(credit_card.expiration_date)
                    )
                case "bank":
                    self.assertEqual(response.data[key], credit_card.bank_id)
                case "payment_system":
                    self.assertEqual(
                        response.data[key],
                        credit_card.payment_system_id
                    )
                case _:
                    self.assertEqual(
                        response.data[key],
                        getattr(credit_card, key)
                    )

    def test_credit_card_creation(self):
        """Test create functionality for credit cards."""
        self.c.force_login(self.user)
        old_number_of_credit_cards = self.user.credit_cards.count()
        new_credit_card_data = {
            "expiration_date": date(2026, 5, 19),
            "bank": 1,
            "payment_system": 1,
            "currency": "USD",
        }
        url = reverse("credit-card-list")
        response = self.c.post(
            url,
            data=new_credit_card_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.user.refresh_from_db()
        self.assertGreater(
            self.user.credit_cards.count(),
            old_number_of_credit_cards
        )

    def test_credit_card_deletion(self):
        """Test delete functionality for credit cards."""
        self.c.force_login(self.user)
        old_number_of_credit_cards = self.user.credit_cards.count()
        credit_card = self.user.credit_cards.first()
        url = reverse("credit-card-detail", kwargs={"pk": credit_card.id})
        response = self.c.delete(url)
        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertGreater(
            old_number_of_credit_cards,
            self.user.credit_cards.count()
        )
