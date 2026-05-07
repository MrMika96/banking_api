"""Module with views for user model."""
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from users.models import Contact, Profile, User
from users.serializers import (
    ContactBulkCreateSerializer,
    ContactSerializer,
    ContactSerializerShort,
    ProfileSerializer,
    RepresentationContactBulkCreateSerializer,
    UpdateContactSerializer,
    UserCredentialsUpdateSerializer,
    UserMeSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from utils.paginations import DynamicPageNumberPagination
from . import docs
from .services.user_services import (
    bulk_create_contacts,
    register_user,
    update_users_credentials
)


@extend_schema_view(**docs.get_user_auth_docs())
class UserAuthView(TokenObtainPairView):
    """View for user authentication in API."""

    serializer_class = TokenObtainPairSerializer


@extend_schema_view(**docs.get_user_auth_refresh_docs())
class UserAuthRefreshView(TokenRefreshView):
    """View what takes refresh token and returns access token."""


@extend_schema_view(**docs.get_user_me_docs())
class UserMeViewSet(viewsets.ModelViewSet):
    """Return info about authenticated user."""

    queryset = User.objects.all()
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return user object with his profile info."""
        qs = super().get_queryset()
        return (
            qs.filter(id=self.request.user.id)
            .select_related("profile")
            .annotate(registered_cards_count=Count("credit_cards"))
            .first()
        )


@extend_schema_view(**docs.get_user_me_profile_docs())
class UserMeProfileView(generics.UpdateAPIView):
    """View for profile of a user."""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        """Return authorized users profile."""
        return self.request.user.profile


@extend_schema_view(**docs.get_user_docs())
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Receive list or a single user object."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DynamicPageNumberPagination

    def get_queryset(self):
        """Return queryset."""
        qs = super().get_queryset()
        return qs.select_related("profile")


@extend_schema_view(**docs.get_user_register_docs())
class UserRegisterView(generics.GenericAPIView):
    """Register user in a system."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Create new user in a system."""
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user = register_user(input_serializer.validated_data)
        output_serializer = self.get_serializer(user)
        return Response(
            data=output_serializer.data,
            status=201
        )


@extend_schema_view(**docs.get_user_credentials_update_docs())
class UserCredentialsUpdateView(generics.GenericAPIView):
    """Update users credentials."""

    queryset = User.objects.all()
    serializer_class = UserCredentialsUpdateSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """Return user with partially update credentials."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            data=self.get_serializer(update_users_credentials(
                user=self.request.user,
                user_data=serializer.validated_data
            )).data,
            status=200
        )


@extend_schema_view(**docs.get_contact_docs())
class ContactViewSet(viewsets.ModelViewSet):
    """View for Contact model."""

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
        """Return queryset."""
        qs = super().get_queryset()
        return (
            qs.filter(user_id=self.request.user.id)
            .select_related(
                "user",
                "user__profile",
                "contact",
                "contact__profile",
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
        """Return serializer based on type of request."""
        if not self.kwargs.get("pk") and self.request.method == "GET":
            return ContactSerializerShort
        if self.request.method == "PUT":
            return UpdateContactSerializer
        return super().get_serializer_class()


@extend_schema_view(**docs.get_user_credentials_bulk_create_docs())
class ContactBulkCreateViewSet(generics.GenericAPIView):
    """Bulk create view for user contacts."""

    queryset = Contact.objects.all()
    serializer_class = ContactBulkCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Bulk create contacts for user."""
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        output_serializer = RepresentationContactBulkCreateSerializer(
            bulk_create_contacts(
                self.request.user,
                input_serializer.validated_data
            )
        )
        return Response(
            data=output_serializer.data,
            status=201
        )
