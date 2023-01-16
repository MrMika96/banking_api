from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError


class UserManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    @staticmethod
    def normalize_email(email):
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except (ValueError, AttributeError):
            pass
        else:
            email = f"{email_name}@{domain_part}".lower()
        return email

    @atomic
    def _register(self, password: str, profile: dict, email: str) -> "User":
        email = self.normalize_email(email)
        user = self.create(email=email)

        Profile.objects.create(
            user=user,
            **profile
        )

        user.set_password(password)
        user.save()
        return user

    def register(self, password: str, email: str, profile: dict):
        return self._register(password=password, profile=profile, email=email)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True, editable=False)
    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"
        ordering = ["id"]


class Profile(models.Model):
    last_name = models.CharField(max_length=64, blank=True, null=False)
    first_name = models.CharField(max_length=64, blank=True, null=False)
    middle_name = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE, primary_key=True)

    class Meta:
        db_table = "profiles"
        ordering = ["last_name"]
        indexes = [
            models.Index(fields=["first_name"]),
            models.Index(fields=["middle_name"]),
            models.Index(fields=["last_name"]),
        ]

    @staticmethod
    def check_phone_len(phone):
        """Phone len must be greater or equal than 5 digits and less or equal than 19.
         If it is not, returns False"""
        if phone.isdigit():
            return 5 <= len(phone) <= 19
        return 5 <= len(phone[1:]) <= 19

    @classmethod
    def normalize_phone(cls, phone):
        characters_to_remove = ["-", " ", ".", "*", "(", ")", "/"]
        for character in characters_to_remove:
            phone = phone.replace(character, "")
        if not cls.check_phone_len(phone):
            msg = "Phone number must be between 5 and 19 characters!"
            raise ValidationError(msg)

        if phone.startswith("8") and len(phone) == 11 and phone.isdigit():
            return "+7" + phone[1:]
        elif phone.startswith("+7") and len(phone) == 12 and phone[1:].isdigit():
            return phone
        elif phone.startswith("+") and phone[1:].isdigit():
            return phone
        elif phone.isdigit():
            return "+" + phone
        else:
            msg = "The phone number must contain only numbers and start with a plus sign!"
            raise ValidationError(msg)


class Contact(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='contacts')
    contact = models.ForeignKey('User', on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)
    invitation_counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(null=True, auto_now_add=True, editable=False)

    class Meta:
        unique_together = ['user', 'contact']
