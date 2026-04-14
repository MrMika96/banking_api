"""Module with documentation for views."""
from drf_spectacular.utils import extend_schema


AUTH_TAG = "Authentication"
USERS_TAG = "Users"


def get_user_auth_docs() -> dict:
    """Return documentation for user auth in a system."""
    return {
        "post": extend_schema(
            tags=[AUTH_TAG],
            description="Takes a set of user credentials and returns "
                        "an access and refresh JSON web token pair "
                        "to prove the authentication of those credentials.",
            summary="User authorization in the system",
        )
    }


def get_user_auth_refresh_docs() -> dict:
    """Return documentation for user refresh token generation."""
    return {
        "post": extend_schema(
            tags=[AUTH_TAG],
            description="Takes a refresh type JSON web token and returns an "
                        "access type JSON web token "
                        "if the refresh token is valid.",
            summary="Get new access token from refresh token",
        )
    }


def get_user_me_docs() -> dict:
    """Return documentation for authenticated users info."""
    return {
        "retrieve": extend_schema(
            tags=[USERS_TAG],
            description="Route for viewing your own information",
            summary="Get authorized user data",
        ),
        "update": extend_schema(
            tags=[USERS_TAG],
            description="Route for updating your profile information",
            summary="Update authorized user data",
        ),
        "destroy": extend_schema(
            tags=[USERS_TAG],
            description="Route for deletion of your own account from system",
            summary="delete authorized user",
        ),
    }


def get_contact_docs() -> dict:
    """Return documentation about contacts in a system."""
    return {
        "list": extend_schema(
            tags=[USERS_TAG],
            description="Route for obtaining a list of "
                        "opponents of a user authorized in the system",
            summary="Get all user contacts",
        ),
        "retrieve": extend_schema(
            tags=[USERS_TAG],
            description="Route to get a specific contact by its id",
            summary="Get a contact"
        ),
        "create": extend_schema(
            tags=[USERS_TAG],
            description="Route to add one user to the contact list",
            summary="Adding a contact",
        ),
        "update": extend_schema(
            tags=[USERS_TAG],
            description="Route to change the status of a contact "
                        "(favorite or not) by its id",
            summary="Changing the status of a contact",
        ),
        "destroy": extend_schema(
            tags=[USERS_TAG],
            description="Route to remove a user from "
                        "the contact list by his id",
            summary="Deleting a contact",
        ),
    }


def get_user_docs() -> dict:
    """Return documentation for users in a system."""
    return {
        "list": extend_schema(
            tags=[USERS_TAG],
            description="Route for viewing all users who have "
                        "been registered in the system",
            summary="View all users",
        ),
        "retrieve": extend_schema(
            tags=[USERS_TAG],
            description="Route for viewing specific users, via user id,  "
                        "who have been registered in the system",
            summary="View specific user",
        ),
    }


def get_user_register_docs() -> dict:
    """Return documentation about user registration in a system."""
    return {
        "post": extend_schema(
            tags=[USERS_TAG],
            description="User system registration, takes users email, "
                        "password and profile data and saves it in our system",
            summary="User registration in the system",
        )
    }


def get_user_credentials_update_docs() -> dict:
    """Return documentation about users credentials update."""
    return {
        "put": extend_schema(
            tags=[USERS_TAG],
            description="This route is only for changing "
                        "authorized user email and password",
            summary="Authorized user credentials update",
        )
    }


def get_user_credentials_bulk_create_docs() -> dict:
    """Return documentation about bulk creation of contacts for user."""
    return {
        "post": extend_schema(
            tags=[USERS_TAG],
            description="Route for uploading a bunch of users (by their "
                        "phone number) to the authorized user's contact list",
            summary="Upload a pack of contacts",
        )
    }
