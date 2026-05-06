"""Module for e2e testing for users app."""
from django.urls import reverse
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from users.models import User


class BaseTenantTestCase(TenantTestCase):
    """Parent class for all tests."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()

        self.tenant.save()
        self.domain.save()
        self.c = TenantClient(self.tenant)


class TestAccessRefreshTokens(BaseTenantTestCase):
    """Test suite for JWT access and refresh token authentication flow."""

    def setUp(self):
        """Set up test environment before each test method."""
        super().setUp()

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


class TestUserEndpoints(BaseTenantTestCase):
    """Test class for routes '/user/' and '/user/me/'."""

    def setUp(self):
        """Set up method for tests."""
        super().setUp()

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
        dummy_user_data = {
            "email": "user%d@test.com",
            "password": "Test123456"
        }
        for i in range(10):
            User.objects.create(
                email=dummy_user_data["email"] % i,
                password=dummy_user_data["password"]
            )

    def test_user_register(self):
        """Test new user registration in a system."""
        url = reverse("user-register")
        data = {
            "email": "register@test.com",
            "password": "register_user123",
            "profile": {
                "first_name": "Register",
                "middle_name": "User",
                "last_name": "Test",
                "phone": "+71112223344",
                "birth_date": "1980-05-06"
            }
        }
        response = self.c.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_get_users_list(self):
        """Test getting the list of all system users."""
        self.c.force_login(self.user)
        response = self.c.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], User.objects.count())

    def test_get_user_by_id(self):
        """Test getting the list of all system users."""
        self.c.force_login(self.user)
        response = self.c.get(reverse("user-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

    def test_user_change_credentials(self):
        """Test the ability of a user to change his own credentials."""
        self.c.force_login(self.user)
        url = reverse("user-change-credentials")
        data = {
            "email": "new_user_email@example.com",
            "old_password": self.test_user_data["password"],
            "password": "Very_new_password_123"
        }
        response = self.c.patch(url, data, content_type="application/json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)
