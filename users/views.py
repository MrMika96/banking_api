from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from . import docs
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


@extend_schema_view(**docs.get_user_auth_docs())
class UserAuthView(TokenObtainPairView):
    """View for user authentication in API."""
    serializer_class = UserTokenObtainPairSerializer


@extend_schema_view(**docs.get_user_auth_refresh_docs())
class UserAuthRefreshView(TokenRefreshView):
    """View what takes refresh token and returns access token. """


@extend_schema_view(**docs.get_user_me_docs())
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


@extend_schema_view(**docs.get_user_docs())
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("profile")


@extend_schema_view(**docs.get_user_register_docs())
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


@extend_schema_view(**docs.get_user_credentials_update_docs())
class UserCredentialsUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCredentialsUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user


@extend_schema_view(**docs.get_contact_docs())
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
        return super().get_serializer_class()


@extend_schema_view(**docs.get_user_credentials_bulk_create_docs())
class ContactBulkCreateViewSet(generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactBulkCreateSerializer
    permission_classes = [IsAuthenticated]
