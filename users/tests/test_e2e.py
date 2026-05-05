"""Module for e2e testing for users app."""
from django.urls import reverse
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from users.models import User


class TestAccessRefreshTokens(TenantTestCase):
    """Test suite for JWT access and refresh token authentication flow."""

    def setUp(self):
        """Set up test environment before each test method."""
        super().setUp()

        self.tenant.save()
        self.domain.save()

        self.c = TenantClient(self.tenant)
        self.test_user_data = {
            "email": "user@test.com",
            "password": "test123456",
            "profile": {
                "first_name": "Test",
                "middle_name": "Test",
                "last_name": "Test",
                "phone": "+79990008877",
                "birth_date": timezone.now().date()
            }
        }
        self.user = User.objects.register(**self.test_user_data)

    def test_receiving_access_and_refresh(self):
        """Test that user can obtain both access and refresh tokens."""
        url = reverse("user-auth")
        data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        response = self.c.post(
            url,
            data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_receiving_access_from_refresh(self):
        """Test that user can get access token using a refresh token."""
        url = reverse("user-auth")
        data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        response = self.c.post(
            url,
            data,
            content_type="application/json"
        )
        self.assertIn("access", response.data)

        url = reverse("user-refresh")
        data = {"refresh": response.data["refresh"]}
        response = self.c.post(
            url,
            data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
