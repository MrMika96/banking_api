from collections import OrderedDict
from typing import TYPE_CHECKING

from ..repository.user_repositories import UserRepository

if TYPE_CHECKING:
    from ..models import User


def register_user(user_data: OrderedDict) -> "User":
    """Service for user registration."""
    return UserRepository().register_user(user_data)
