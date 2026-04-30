"""repository module for user app."""
from collections import OrderedDict

from ..models import User


class UserRepository:
    """Repository for working with user instances."""

    model = User

    def register_user(self, user_data: OrderedDict) -> User:
        """Register new user in a system."""
        return self.model.objects.register(
            email=user_data["email"],
            password=user_data["password"],
            profile=user_data["profile"],
        )
