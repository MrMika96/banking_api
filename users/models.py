"""Module with models for user app."""
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager as DefaultUserManager
from django.db import models
from django.db.transaction import atomic
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class UserManager(models.Manager):
    """Custom manager for a user model."""

    def get_by_natural_key(self, username):
        """Get user by natural key."""
        return self.get(**{self.model.USERNAME_FIELD: username})

    @staticmethod
    def normalize_email(email):
        """Normalize users email."""
        return DefaultUserManager.normalize_email(email)

    @atomic
    def _register(self, password: str, profile: dict, email: str) -> "User":
        email = self.normalize_email(email)
        user = self.create(email=email)

        Profile.objects.create(user=user, **profile)

        user.set_password(password)
        user.save()
        return user

    def register(self, password: str, email: str, profile: dict):
        """Register new user in a system."""
        return self._register(password=password, profile=profile, email=email)


class User(AbstractBaseUser):
    """Model of a user."""

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(
        null=True, auto_now_add=True, editable=False
    )
    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        """Meta."""

        db_table = "users"
        ordering = ["id"]


class Profile(models.Model):
    """
    Profile of a user.

    Contains users personal data.
    """

    last_name = models.CharField(max_length=64, blank=True, null=False)
    first_name = models.CharField(max_length=64, blank=True, null=False)
    middle_name = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    user = models.OneToOneField(
        "User",
        related_name="profile",
        on_delete=models.CASCADE,
        primary_key=True
    )
    profile_image = models.OneToOneField(
        "images.Image",
        related_name="profile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None
    )

    class Meta:
        """Meta."""

        db_table = "profiles"
        ordering = ["last_name"]
        indexes = [
            models.Index(fields=["first_name"]),
            models.Index(fields=["middle_name"]),
            models.Index(fields=["last_name"]),
        ]

    @property
    def age(self) -> int | None:
        """Calculate users age."""
        if self.birth_date:
            today = timezone.now().date()
            is_birthday_not_yet = (
                    (today.month, today.day) <
                    (self.birth_date.month, self.birth_date.day)
            )
            return today.year - self.birth_date.year - is_birthday_not_yet
        return None

    @staticmethod
    def check_phone_len(phone):
        """Check phone number length."""
        if phone.isdigit():
            return 5 <= len(phone) <= 19
        return 5 <= len(phone[1:]) <= 19

    @classmethod
    def normalize_phone(cls, phone):
        """Normalize users phone number."""
        characters_to_remove = ["-", " ", ".", "*", "(", ")", "/"]
        for character in characters_to_remove:
            phone = phone.replace(character, "")
        if not cls.check_phone_len(phone):
            msg = "Phone number must be between 5 and 19 characters!"
            raise ValidationError(msg)
        if phone.startswith("8") and len(phone) == 11 and phone.isdigit():
            return "+7" + phone[1:]
        if (
                phone.startswith("+7") and
                len(phone) == 12 and
                phone[1:].isdigit()
        ):
            return phone
        if phone.startswith("+") and phone[1:].isdigit():
            return phone
        if phone.isdigit():
            return "+" + phone
        msg = (
            "The phone number must contain only "
            "numbers and start with a plus sign!"
        )
        raise ValidationError(msg)

    def save(self, *args, **kwargs):
        """Save new object to database with phone normalization."""
        if self.phone:
            self.phone = self.normalize_phone(self.phone)
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Contact in a user address book."""

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="contacts"
    )
    contact = models.ForeignKey("User", on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)
    invitation_counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(
        null=True, auto_now_add=True, editable=False
    )

    class Meta:
        """Meta."""

        unique_together = ["user", "contact"]
        db_table = "contacts"
