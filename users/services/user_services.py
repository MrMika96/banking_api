"""Service module for user app."""
from collections import OrderedDict
from typing import TYPE_CHECKING

from ..repository.user_repositories import UserRepository

if TYPE_CHECKING:
    from ..models import User


def register_user(user_data: OrderedDict) -> "User":
    """Service for user registration."""
    return UserRepository().register_user(user_data)


def update_users_credentials(user: "User", user_data: OrderedDict) -> "User":
    """Service for users credentials updates."""
    return UserRepository().update_user_credentials(user, user_data)


def bulk_create_contacts(user: "User", contacts_data: OrderedDict) -> dict:
    """Service for bulk creation of contacts for user."""
    contacts = UserRepository().bulk_create_contacts(user, contacts_data)
    return {
        "count": len(contacts),
        "results": contacts
    }
