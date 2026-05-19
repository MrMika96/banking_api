"""Module for e2e testing for users app."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from users.models import Contact, Profile

User = get_user_model()


class BaseUsersTenantTestCase(TenantTestCase):
    """Parent class for all tests."""

    def setUp(self):
        """Set up test environment."""
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


class TestAccessRefreshTokens(BaseUsersTenantTestCase):
    """Test suite for JWT access and refresh token authentication flow."""

    def setUp(self):
        """Set up test environment before each test method."""
        super().setUp()

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


class TestUserEndpoints(BaseUsersTenantTestCase):
    """Test class for routes '/user/'."""

    def setUp(self):
        """Set up method for tests."""
        super().setUp()
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


class TestUserMeEndpoints(BaseUsersTenantTestCase):
    """Test class for routes '/user/me/'."""

    def setUp(self):
        """Set up method for tests."""
        super().setUp()

    def test_get_users_own_data(self):
        """Test if it`s possible for user to get his own data."""
        self.c.force_login(self.user)
        url = reverse("user-data")
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)

    def test_change_users_own_data(self):
        """Test if it`s possible for user to update his own data."""
        self.c.force_login(self.user)
        url = reverse("user-profile-update")
        data = {
            "first_name": "New_name",
            "middle_name": "New_middle_name",
            "last_name": "New_last_name",
            "phone": "+78005553535",
            "birth_date": timezone.now().date() - timedelta(days=1)
        }
        response = self.c.patch(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        for key in data:
            self.assertEqual(
                data[key],
                getattr(self.user.profile, key)
            )

    def test_user_hard_delete(self):
        """Test if it`s possible for user to delete himself from system."""
        self.c.force_login(self.user)
        url = reverse("user-data")
        response = self.c.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())


class TestUserContacts(BaseUsersTenantTestCase):
    """Tests for user contacts functionality."""

    def setUp(self):
        """Set up method for tests."""
        super().setUp()
        dummy_user_data = {
            "email": "user%d@test.com",
            "password": "test123456"
        }
        for i in range(10):
            dummy_user_profile = {
                "first_name": "Test%d" % i,
                "middle_name": "Test%d" % i,
                "last_name": "Test%d" % i,
                "phone": "+7999000887%d" % i,
                "birth_date": timezone.now().date()
            }
            User.objects.register(
                email=dummy_user_data["email"] % i,
                password=dummy_user_data["password"],
                profile=dummy_user_profile
            )
        for future_contact in User.objects.all()[:5]:
            Contact.objects.create(user=self.user, contact=future_contact)

    def test_get_users_contact_list(self):
        """Testing getting full list of user contacts."""
        self.c.force_login(self.user)
        url = reverse("contacts-list")
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_new_contact(self):
        """Testing adding new contact to user contacts."""
        self.c.force_login(self.user)
        old_number_of_contacts = self.user.contacts.count()
        contact_list = list(
            self.user.contacts.values_list("contact_id", flat=True)
        )
        new_contact = User.objects.filter(~Q(id__in=contact_list)).first()
        url = reverse("contacts-list")
        data = {
            "contact_id": new_contact.id,
            "favorite": True
        }
        response = self.c.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertGreater(
            self.user.contacts.count(),
            old_number_of_contacts,
            msg="Number of users contacts did not increase"
        )

    def test_remove_users_contact(self):
        """Testing removing unwanted contact from user contacts."""
        self.c.force_login(self.user)
        old_number_of_contacts = self.user.contacts.count()
        contact_to_remove = self.user.contacts.first()
        url = reverse("contacts-detail", kwargs={"pk": contact_to_remove.id})
        response = self.c.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertGreater(
            old_number_of_contacts,
            self.user.contacts.count(),
            msg="Number of users contacts did not decrease"
        )

    def test_changing_favorite_status_of_a_contact(self):
        """Test functionality of making users contact favorite."""
        self.c.force_login(self.user)
        contact_to_make_favorite = self.user.contacts.first()
        url = reverse(
            "contacts-detail",
            kwargs={"pk": contact_to_make_favorite.id}
        )
        data = {"favorite": True}
        response = self.c.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            self.user.contacts.get(id=contact_to_make_favorite.id).favorite
        )

    def test_contacts_bulk_creation(self):
        """Testing contact bulk creation functionality."""
        self.c.force_login(self.user)
        old_number_of_contacts = self.user.contacts.count()
        url = reverse("user-contacts-bulk-create")
        data = {
            "phone_numbers":
                list(
                    Profile.objects.exclude(user=self.user).values_list(
                        "phone", flat=True
                    )
                )
        }
        response = self.c.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertGreater(
            self.user.contacts.count(),
            old_number_of_contacts,
            msg="Number of users contacts did not increase"
        )
