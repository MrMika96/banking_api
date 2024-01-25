import datetime

from django.contrib.auth.models import update_last_login
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from images.serializers import ImageSerializer
from users.models import User, Profile, Contact


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        self.user = get_object_or_404(User, email=attrs["email"])
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise NotFound(detail="User not found")
        return email

    def validate_password(self, password):
        user = get_object_or_404(User, email=self.initial_data["email"])
        if not user.check_password(password):
            raise ValidationError(detail="Incorrect password")
        return password


class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "phone",
            "birth_date",
            "age",
        ]

    def validate_phone(self, phone):
        if phone:
            phone = self.Meta.model.normalize_phone(phone)
        return phone

    @extend_schema_field({"type": "string"})
    def get_age(self, obj):
        return (
            datetime.datetime.utcnow().year - obj.birth_date.year
            if obj.birth_date
            else ""
        )


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "email", "password", "profile"]
        read_only_fields = ["id"]

    def validate_email(self, email):
        if self.Meta.model.objects.filter(email=email).exists():
            raise ValidationError(detail="User with that email already exists")
        return self.Meta.model.objects.normalize_email(email)

    def create(self, validated_data):
        return User.objects.register(
            email=validated_data["email"],
            password=validated_data["password"],
            profile=validated_data["profile"],
        )


class UserMeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(help_text="Contains user's personal data")
    registered_cards_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "profile", "registered_cards_count"]
        read_only_fields = ["id", "email"]

    def update(self, instance, validated_data):
        super().update(instance.profile, validated_data.pop("profile"))
        return instance


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(help_text="Contains user's personal data")

    class Meta:
        model = User
        fields = ["id", "email", "profile"]
        read_only_fields = ["id", "email"]


class UserCredentialsUpdateSerializer(serializers.ModelSerializer):
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
        model = User
        fields = ["email", "password", "old_password"]

    def validate_email(self, email):
        if self.Meta.model.objects.filter(email=email).exists():
            raise ValidationError("User with that email already exists")
        return self.Meta.model.objects.normalize_email(email)

    def validate_password(self, password):
        if self.initial_data.get("old_password") and self.context[
            "request"
        ].user.check_password(self.initial_data["old_password"]):
            if password and self.initial_data["old_password"] == password:
                raise ValidationError("New password is the same as an old one")
            elif not password and self.initial_data["old_password"] == password:
                raise ValidationError("To change password you must enter new one")
        elif self.initial_data.get("old_password") and not self.context[
            "request"
        ].user.check_password(self.initial_data["old_password"]):
            raise ValidationError("Old password you entered was incorrect")
        return password

    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        if validated_data.get("password") and validated_data.get("old_password"):
            instance.set_password(validated_data["password"])
        instance.save()
        return instance


class MaintainerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="profile.first_name", read_only=True)
    last_name = serializers.CharField(source="profile.last_name", read_only=True)
    phone = serializers.CharField(source="profile.phone", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "phone", "first_name", "last_name"]


class ContactProfileSerializer(serializers.ModelSerializer):
    contact_id = serializers.IntegerField(source="user_id", read_only=True)
    image = ImageSerializer(allow_null=True, read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
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
    contact_id = serializers.IntegerField(source="user_id", read_only=True)
    image = ImageSerializer(allow_null=True, read_only=True)

    class Meta:
        model = Profile
        fields = ["contact_id", "first_name", "last_name", "image"]


class ContactSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contact = ContactProfileSerializer(read_only=True, source="contact.profile")
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="contact"
    )

    class Meta:
        model = Contact
        fields = ["id", "user", "contact", "contact_id", "favorite", "created_at"]

    def validate_contact_id(self, contact_id):
        user = self.context["request"].user
        if user.id == contact_id.id:
            raise ValidationError("You can`t add your own account to contacts")
        if (
            self.context["request"].method == "POST"
            and self.Meta.model.objects.filter(user=user, contact=contact_id).exists()
        ):
            raise ValidationError("This contact already exists")
        return contact_id


class ContactSerializerShort(serializers.ModelSerializer):
    contact = ContactProfileShortSerializer(read_only=True, source="contact.profile")

    class Meta:
        model = Contact
        fields = ["id", "contact", "favorite"]


class ContactBulkCreateSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    phone_numbers = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True,
        allow_empty=False,
        help_text="Phone numbers of users to be added to the contact list",
    )

    def validate_phone_numbers(self, phone_numbers):
        normalized_phones = []
        for phone_number in set(phone_numbers):
            normalized_phones.append(Profile.normalize_phone(phone_number))
        if self.context["request"].user.profile.phone in normalized_phones:
            normalized_phones.remove(self.context["request"].user.profile.phone)
        if not User.objects.filter(profile__phone__in=normalized_phones).exists():
            raise NotFound("Phone number not found")
        return normalized_phones

    def to_representation(self, instance):
        response = dict()
        response["count"] = len(instance)
        response["results"] = ContactSerializerShort(instance=instance, many=True).data
        return response

    @atomic
    def create(self, validated_data):
        current_user = validated_data["user"]
        users = User.objects.filter(
            profile__phone__in=validated_data["phone_numbers"]
        ).values_list("id", flat=True)
        results = []
        for user in users:
            contact, created = Contact.objects.get_or_create(
                user=current_user, contact_id=user
            )
            results.append(contact)
