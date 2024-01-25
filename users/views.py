from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User, Contact
from users.serializers import (
    UserTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserCredentialsUpdateSerializer,
    ContactSerializerShort,
    ContactSerializer,
    ContactBulkCreateSerializer,
    UserMeSerializer,
)
from utils.paginations import DynamicPageNumberPagination


@extend_schema_view(
    post=extend_schema(
        description="Takes a set of user credentials and returns "
        "an access and refresh JSON web token pair "
        "to prove the authentication of those credentials.",
        summary="User authorization in the system",
    )
)
class UserAuthView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


@extend_schema_view(
    retrieve=extend_schema(
        description="Route for viewing your own information",
        summary="Get authorized user data",
    ),
    update=extend_schema(
        description="Route for updating your profile information",
        summary="Update authorized user data",
    ),
    destroy=extend_schema(
        description="Route for deletion of your own account from system",
        summary="delete authorized user",
    ),
)
class UserMeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        qs = super().get_queryset()

        return (
            qs.filter(id=self.request.user.id)
            .select_related("profile")
            .annotate(registered_cards_count=Count("credit_cards"))
            .first()
        )


@extend_schema_view(
    list=extend_schema(
        description="Route for viewing all users who have been registered in the system",
        summary="View all users",
    ),
    retrieve=extend_schema(
        description="Route for viewing specific users, via user id,  "
        "who have been registered in the system",
        summary="View specific user",
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.select_related("profile")

    def get_permissions(self):
        if self.action == "user_register":
            return [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "user_register":
            return UserRegisterSerializer

        return super().get_serializer_class()

    @extend_schema(
        request=UserRegisterSerializer,
        responses=UserRegisterSerializer,
        description="User system registration, takes users email, "
        "password and profile data and saves it in our system",
        summary="User registration in the system",
    )
    @action(methods=["post"], url_name="register", url_path="register", detail=False)
    def user_register(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema_view(
    put=extend_schema(
        description="This route is only for changing authorized user email and password",
        summary="Authorized user credentials update",
    )
)
class UserCredentialsUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCredentialsUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user


@extend_schema_view(
    list=extend_schema(
        description="Route for obtaining a list of opponents of a user authorized in the system",
        summary="Get all user contacts",
    ),
    retrieve=extend_schema(
        description="Route to get a specific contact by its id", summary="Get a contact"
    ),
    create=extend_schema(
        description="Route to add one user to the contact list",
        summary="Adding a contact",
    ),
    update=extend_schema(
        description="Route to change the status of a contact (favorite or not) by its id",
        summary="Changing the status of a contact",
    ),
    destroy=extend_schema(
        description="Route to remove a user from the contact list by his id",
        summary="Deleting a contact",
    ),
)
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    pagination_class = DynamicPageNumberPagination
    search_fields = [
        "contact__profile__last_name",
        "contact__profile__first_name",
        "contact__profile__middle_name",
        "contact__profile__phone",
        "contact__email",
    ]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == "bulk_create_contacts":
            return qs
        return (
            qs.filter(user_id=self.request.user.id)
            .select_related(
                "user",
                "user__profile",
                "user__profile__image",
                "contact",
                "contact__profile",
                "contact__profile__image",
            )
            .order_by(
                "-favorite",
                "-invitation_counter",
                "contact__profile__last_name",
                "contact__profile__first_name",
                "contact__profile__middle_name",
                "id",
            )
        )

    def get_serializer_class(self):
        if not self.kwargs.get("pk") and self.request.method == "GET":
            return ContactSerializerShort
        if self.action == "bulk_create_contacts":
            return ContactBulkCreateSerializer

        return super().get_serializer_class()

    @extend_schema(
        responses=ContactBulkCreateSerializer,
        request=ContactBulkCreateSerializer,
        description="Route for uploading a bunch of users (by their phone number) "
        "to the authorized user's contact list",
        summary="Download a pack of contacts",
    )
    @action(
        url_path="bulk_create_contacts",
        url_name="bulk_create_contacts",
        methods=["post"],
        detail=False,
    )
    def bulk_create_contacts(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
