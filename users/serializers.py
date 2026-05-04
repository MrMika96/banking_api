"""Serialization module for users."""
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

from images.serializers import ImageSerializer
from users.models import Contact, Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for a profile."""

    image = ImageSerializer(allow_null=True, read_only=True)

    class Meta:
        """Meta."""

        model = Profile
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "phone",
            "birth_date",
            "age",
            "image"
        ]

    def validate_phone(self, phone: str):
        """Validate phone number."""
        return self.Meta.model.normalize_phone(phone) if phone else phone


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for users registration in a system."""

    password = serializers.CharField(
        write_only=True, required=True, min_length=8
    )
    profile = ProfileSerializer()

    class Meta:
        """Meta."""

        model = User
        fields = ["id", "email", "password", "profile"]
        read_only_fields = ["id"]

    def validate_email(self, email):
        """Validate users email."""
        if self.Meta.model.objects.filter(email=email).exists():
            raise ValidationError(detail="User with that email already exists")
        return self.Meta.model.objects.normalize_email(email)


class UserMeSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user."""

    profile = ProfileSerializer(help_text="Contains user's personal data")
    registered_cards_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta."""

        model = User
        fields = ["id", "email", "profile", "registered_cards_count"]
        read_only_fields = ["id", "email"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for a user."""

    profile = ProfileSerializer(help_text="Contains user's personal data")

    class Meta:
        """Meta."""

        model = User
        fields = ["id", "email", "profile"]
        read_only_fields = ["id", "email"]


class UserCredentialsUpdateSerializer(serializers.Serializer):
    """Serializer for user credentials."""

    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        help_text="This field is required for password changing. "
        "Field should contain new password",
    )
    old_password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        help_text="This field is required for password changing. "
        "Field should contain old password",
    )

    class Meta:
        """Meta."""

        model = User
        fields = ["email", "password", "old_password"]

    def validate_email(self, email: str) -> str:
        """Validate entered email."""
        if self.Meta.model.objects.filter(email=email).exists():
            raise ValidationError("User with that email already exists")
        return self.Meta.model.objects.normalize_email(email)

    def validate_password(self, password: str) -> str:
        """Validate entered password."""
        old_password = self.initial_data.get("old_password")
        user = self.context["request"].user
        if not old_password:
            return password
        if not user.check_password(old_password):
            raise ValidationError("Old password you entered was incorrect")
        if password == old_password:
            raise ValidationError("New password is the same as an old one")
        if not password:
            raise ValidationError("To change password you must enter new one")
        return password


class MaintainerSerializer(serializers.ModelSerializer):
    """Serializer for a maintainer."""

    first_name = serializers.CharField(
        source="profile.first_name", read_only=True
    )
    last_name = serializers.CharField(
        source="profile.last_name", read_only=True
    )
    phone = serializers.CharField(source="profile.phone", read_only=True)

    class Meta:
        """Meta."""

        model = User
        fields = ["id", "email", "phone", "first_name", "last_name"]


class ContactProfileSerializer(serializers.ModelSerializer):
    """Serializer for a contacts profile."""

    contact_id = serializers.IntegerField(source="user_id", read_only=True)
    image = ImageSerializer(allow_null=True, read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        """Meta."""

        model = Profile
        fields = [
            "contact_id",
            "first_name",
            "middle_name",
            "last_name",
            "image",
            "email",
            "phone",
        ]


class ContactProfileShortSerializer(serializers.ModelSerializer):
    """Short serializer for a contacts profile."""

    contact_id = serializers.IntegerField(source="user_id", read_only=True)
    image = ImageSerializer(allow_null=True, read_only=True)

    class Meta:
        """Meta."""

        model = Profile
        fields = ["contact_id", "first_name", "last_name", "image"]


class ContactSerializer(serializers.ModelSerializer):
    """Serializer class for user contacts."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contact = ContactProfileSerializer(
        read_only=True, source="contact.profile"
    )
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="contact"
    )

    class Meta:
        """Meta."""

        model = Contact
        fields = [
            "id",
            "user",
            "contact",
            "contact_id",
            "favorite",
            "created_at"
        ]

    def validate_contact_id(self, contact_id):
        """Validate id of a users contact."""
        user = self.context["request"].user
        if user.id == contact_id.id:
            raise ValidationError("You can`t add your own account to contacts")
        if (
            self.context["request"].method == "POST"
            and self.Meta.model.objects.filter(
                user=user, contact=contact_id
            ).exists()
        ):
            raise ValidationError("This contact already exists")
        return contact_id


class ContactSerializerShort(serializers.ModelSerializer):
    """Short serializer for users contacts."""

    contact = ContactProfileShortSerializer(
        read_only=True, source="contact.profile"
    )

    class Meta:
        """Meta."""

        model = Contact
        fields = ["id", "contact", "favorite"]


class ContactBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk create of contacts."""

    phone_numbers = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True,
        allow_empty=False,
        help_text="Phone numbers of users to be added to the contact list",
    )

    def validate_phone_numbers(self, phone_numbers):
        """Validate users phone number."""
        normalized_phones = []
        for phone_number in set(phone_numbers):
            normalized_phones.append(Profile.normalize_phone(phone_number))
        if self.context["request"].user.profile.phone in normalized_phones:
            normalized_phones.remove(
                self.context["request"].user.profile.phone
            )
        if not User.objects.filter(
                profile__phone__in=normalized_phones
        ).exists():
            raise NotFound("Phone number not found")
        return normalized_phones


class RepresentationContactBulkCreateSerializer(serializers.Serializer):
    """Representation serializer for contacts bulk create."""

    count = serializers.IntegerField(min_value=0, default=0)
    results = ContactSerializerShort(many=True)
