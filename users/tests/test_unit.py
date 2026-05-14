"""Unit tests for user repositories module."""
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.utils import timezone

from ..models import Contact
from ..repositories.user_repositories import UserRepository

User = get_user_model()


class UserRepositoryRegisterTest(TestCase):
    """Tests for register_user method."""

    def setUp(self):
        """Set up test environment."""
        self.repository = UserRepository()
        self.valid_data = OrderedDict({
            "email": "test@example.com",
            "password": "testpass123",
            "profile": {
                "first_name": "Test",
                "middle_name": "Testovich",
                "last_name": "Testov",
                "phone": "+79990008877",
                "birth_date": "1990-01-01"
            }
        })

    def test_register_user_success(self):
        """Test successful user registration."""
        user = self.repository.register_user(self.valid_data)

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.first_name, "Test")
        self.assertEqual(user.profile.last_name, "Testov")

    def test_register_user_duplicate_email(self):
        """Test registration with existing email."""
        self.repository.register_user(self.valid_data)

        with self.assertRaises(Exception):
            self.repository.register_user(self.valid_data)

    def test_register_user_missing_email(self):
        """Test registration without email."""
        invalid_data = self.valid_data.copy()
        del invalid_data["email"]

        with self.assertRaises(KeyError):
            self.repository.register_user(invalid_data)


class UserRepositoryUpdateCredentialsTest(TestCase):
    """Tests for update_user_credentials method."""

    def setUp(self):
        """Set up test environment."""
        self.repository = UserRepository()
        test_user_data = {
            "email": "old@example.com",
            "password": "oldpass123",
            "profile": {
                "first_name": "Test",
                "middle_name": "Test",
                "last_name": "Test",
                "phone": "+79990008877",
                "birth_date": timezone.now().date()
            }
        }
        self.user = User.objects.register(**test_user_data)
        self.valid_data = {
            "email": "new@example.com",
            "password": "newpass123",
            "old_password": "oldpass123"
        }

    def test_update_email_success(self):
        """Test successful email update."""
        data = OrderedDict({"email": "updated@example.com"})
        updated_user = self.repository.update_user_credentials(self.user, data)
        self.assertEqual(updated_user.email, "updated@example.com")

    def test_update_password_success(self):
        """Test successful password update."""
        data = OrderedDict({
            "password": "newpassword456",
            "old_password": "oldpass123"
        })
        updated_user = self.repository.update_user_credentials(self.user, data)
        self.assertTrue(updated_user.check_password("newpassword456"))

    def test_update_without_changes(self):
        """Test update without any changes."""
        updated_user = self.repository.update_user_credentials(
            self.user, OrderedDict({})
        )
        self.assertEqual(updated_user.email, "old@example.com")
        self.assertTrue(updated_user.check_password("oldpass123"))

    def test_update_email_only(self):
        """Test updating only email."""
        data = OrderedDict({"email": "newemail@example.com"})
        updated_user = self.repository.update_user_credentials(self.user, data)
        self.assertEqual(updated_user.email, "newemail@example.com")
        self.assertTrue(updated_user.check_password("oldpass123"))

    def test_update_invalid_email(self):
        """Test update with invalid email format."""
        data = OrderedDict({"email": "not-an-email"})
        with self.assertRaises(DjangoValidationError):
            self.repository.update_user_credentials(self.user, data)


class UserRepositoryBulkCreateContactsTest(TestCase):
    """Tests for bulk_create_contacts method."""

    def setUp(self):
        """Set up test environment."""
        self.repository = UserRepository()
        main_user_data = {
            "email": "main@example.com",
            "password": "mainpass123",
            "profile": {
                "first_name": "Main",
                "middle_name": "Mainovich",
                "last_name": "User",
                "phone": "+79990008870",
                "birth_date": timezone.now().date()
            }
        }
        self.user = User.objects.register(**main_user_data)
        contact1_data = {
            "email": "contact1@example.com",
            "password": "contactpass123",
            "profile": {
                "first_name": "Contact",
                "middle_name": "Contactovich",
                "last_name": "One",
                "phone": "+79990008871",
                "birth_date": timezone.now().date()
            }
        }
        self.user1 = User.objects.register(**contact1_data)
        contact2_data = {
            "email": "contact2@example.com",
            "password": "contactpass123",
            "profile": {
                "first_name": "Contact",
                "middle_name": "Contactovich",
                "last_name": "Two",
                "phone": "+79990008872",
                "birth_date": timezone.now().date()
            }
        }
        self.user2 = User.objects.register(**contact2_data)
        contact3_data = {
            "email": "contact3@example.com",
            "password": "contactpass123",
            "profile": {
                "first_name": "Contact",
                "middle_name": "Contactovich",
                "last_name": "Three",
                "phone": "+79990008873",
                "birth_date": timezone.now().date()
            }
        }
        self.user3 = User.objects.register(**contact3_data)
        self.valid_data = OrderedDict({
            "phone_numbers": ["+79990008871", "+79990008872"]
        })

    def test_bulk_create_contacts_success(self):
        """Test successful bulk creation of contacts."""
        contacts = self.repository.bulk_create_contacts(
            self.user, self.valid_data
        )
        self.assertEqual(len(contacts), 2)
        self.assertIsInstance(contacts[0], Contact)
        self.assertEqual(contacts[0].user, self.user)
        self.assertEqual(contacts[0].contact, self.user1)
        self.assertEqual(contacts[1].contact, self.user2)

    def test_bulk_create_contacts_no_matches(self):
        """Test when no users match the phone numbers."""
        data = OrderedDict({"phone_numbers": ["+79990008999", "+79990008888"]})
        contacts = self.repository.bulk_create_contacts(self.user, data)
        self.assertEqual(len(contacts), 0)

    def test_bulk_create_contacts_partial_matches(self):
        """Test when some phone numbers match."""
        data = OrderedDict({"phone_numbers": ["+79990008871", "+79990008999"]})
        contacts = self.repository.bulk_create_contacts(self.user, data)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].contact, self.user1)

    def test_bulk_create_contacts_duplicate_contacts(self):
        """Test creating duplicate contacts (should use get_or_create)."""
        # First creation
        self.repository.bulk_create_contacts(self.user, self.valid_data)
        contacts = self.repository.bulk_create_contacts(
            self.user, self.valid_data
        )
        self.assertEqual(len(contacts), 2)
        self.assertEqual(Contact.objects.filter(user=self.user).count(), 2)

    def test_bulk_create_contacts_empty_list(self):
        """Test with empty phone numbers list."""
        data = OrderedDict({"phone_numbers": []})
        contacts = self.repository.bulk_create_contacts(self.user, data)
        self.assertEqual(len(contacts), 0)


class UserRepositoryEdgeCasesTest(TestCase):
    """Tests for edge cases in repositories."""

    def setUp(self):
        """Set up test environment."""
        self.repository = UserRepository()
        test_user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "profile": {
                "first_name": "Test",
                "middle_name": "Testovich",
                "last_name": "Testov",
                "phone": "+79990008899",
                "birth_date": timezone.now().date()
            }
        }
        self.test_user = User.objects.register(**test_user_data)

    def test_update_user_credentials_with_none_values(self):
        """Test update with None values."""
        data = OrderedDict({
            "email": None,
            "password": None,
            "old_password": None
        })
        updated_user = self.repository.update_user_credentials(
            self.test_user, data
        )
        self.assertEqual(updated_user.email, "test@example.com")
        self.assertTrue(updated_user.check_password("testpass123"))

    def test_update_user_credentials_with_none_email_and_valid_password(self):
        """Test update with None email and valid password change."""
        old_password = "testpass123"
        new_password = "newpass456"
        data = OrderedDict({
            "email": None,
            "password": new_password,
            "old_password": old_password
        })
        updated_user = self.repository.update_user_credentials(
            self.test_user, data
        )
        self.assertEqual(updated_user.email, "test@example.com")
        self.assertTrue(updated_user.check_password(new_password))

    def test_register_user_with_full_profile(self):
        """Test registration with complete profile data."""
        data = OrderedDict({
            "email": "full@example.com",
            "password": "pass123",
            "profile": OrderedDict({
                "first_name": "Full",
                "middle_name": "Middle",
                "last_name": "Last",
                "phone": "+1234567890",
                "birth_date": "2000-01-01"
            })
        })

        user = self.repository.register_user(data)

        self.assertEqual(user.email, "full@example.com")
        self.assertTrue(user.check_password("pass123"))
        self.assertEqual(user.profile.first_name, "Full")
        self.assertEqual(user.profile.middle_name, "Middle")
        self.assertEqual(user.profile.last_name, "Last")
        self.assertEqual(user.profile.phone, "+1234567890")
        self.assertEqual(str(user.profile.birth_date), "2000-01-01")

    def test_register_user_with_minimal_profile(self):
        """Test registration with minimal data (only required fields)."""
        data = OrderedDict({
            "email": "minimal@example.com",
            "password": "minpass123",
            "profile": OrderedDict({
                "first_name": "Min",
                "last_name": "Mal",
                "middle_name": "",
                "phone": "",
                "birth_date": None
            })
        })

        user = self.repository.register_user(data)

        self.assertEqual(user.email, "minimal@example.com")
        self.assertEqual(user.profile.first_name, "Min")
        self.assertEqual(user.profile.last_name, "Mal")
        self.assertEqual(user.profile.middle_name, "")
        self.assertEqual(user.profile.phone, "")
        self.assertIsNone(user.profile.birth_date)

    def test_update_user_credentials_with_empty_old_password(self):
        """Test password update without providing old password."""
        new_password = "newpass456"
        data = OrderedDict({
            "password": new_password,
        })
        updated_user = self.repository.update_user_credentials(
            self.test_user, data
        )
        self.assertTrue(updated_user.check_password("testpass123"))

    def test_update_user_credentials_with_incorrect_old_password(self):
        """Test password update with incorrect old password."""
        data = OrderedDict({
            "password": "newpass456",
            "old_password": "wrongpassword"
        })
        updated_user = self.repository.update_user_credentials(
            self.test_user, data
        )
        self.assertTrue(updated_user.check_password("newpass456"))
