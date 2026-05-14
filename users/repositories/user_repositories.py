"""repositories module for user app."""
from collections import OrderedDict

from django.db.transaction import atomic

from ..models import Contact, User


class UserRepository:
    """Repository for working with user instances."""

    model = User

    def register_user(self, validated_data: OrderedDict) -> User:
        """Register new user in a system."""
        return self.model.objects.register(
            email=validated_data["email"],
            password=validated_data["password"],
            profile=validated_data["profile"],
        )

    def update_user_credentials(
        self,
        user_instance: User,
        validated_data: OrderedDict
    ) -> User:
        """Update users credentials."""
        email = validated_data.get("email")
        if email:
            user_instance.email = validated_data["email"]
        if (
                validated_data.get("password") and
                validated_data.get("old_password")
        ):
            user_instance.set_password(validated_data["password"])
        user_instance.full_clean()
        user_instance.save()
        return user_instance

    @atomic
    def bulk_create_contacts(
        self,
        user_instance: User,
        validated_data: OrderedDict
    ) -> list[Contact]:
        """Bulk create users contacts."""
        users = self.model.objects.filter(
            profile__phone__in=validated_data["phone_numbers"]
        ).select_related("profile").values_list("id", flat=True)
        results = []
        for user in users:
            contact, _ = Contact.objects.get_or_create(
                user=user_instance, contact_id=user
            )
            results.append(contact)
        return results
