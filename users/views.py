"""Module with views for user model."""
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from users.models import Contact, User
from users.serializers import (
    ContactBulkCreateSerializer,
    ContactSerializer,
    ContactSerializerShort,
    UserCredentialsUpdateSerializer,
    UserMeSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserTokenObtainPairSerializer,
)
from utils.paginations import DynamicPageNumberPagination
from . import docs
from .services.user_services import register_user


@extend_schema_view(**docs.get_user_auth_docs())
class UserAuthView(TokenObtainPairView):
    """View for user authentication in API."""

    serializer_class = UserTokenObtainPairSerializer


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
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user = register_user(input_serializer.validated_data)
        output_serializer = self.get_serializer(user)
        return Response(
            data=output_serializer.data,
            status=201
        )


@extend_schema_view(**docs.get_user_credentials_update_docs())
class UserCredentialsUpdateView(generics.UpdateAPIView):
    """Update users credentials."""

    queryset = User.objects.all()
    serializer_class = UserCredentialsUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        """Return authenticated user object."""
        return self.request.user


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
        return super().get_serializer_class()


@extend_schema_view(**docs.get_user_credentials_bulk_create_docs())
class ContactBulkCreateViewSet(generics.CreateAPIView):
    """Bulk create view for user contacts."""

    queryset = Contact.objects.all()
    serializer_class = ContactBulkCreateSerializer
    permission_classes = [IsAuthenticated]
