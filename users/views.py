from django.db.models import Count, Case, When, CharField, Value
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User, Contact
from users.serializers import (
    UserTokenObtainPairSerializer, UserRegisterSerializer,
    UserSerializer, UserCredentialsUpdateSerializer, ContactSerializerShort, ContactSerializer,
    ContactBulkCreateSerializer
)
from utils.paginations import DynamicPageNumberPagination


@extend_schema_view(
    post=extend_schema(description="Takes a set of user credentials and returns "
                                   "an access and refresh JSON web token pair "
                                   "to prove the authentication of those credentials.",
                       summary="User authorization in the system"
                       )
)
class UserAuthView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(description="User system registration, takes users email, "
                                   "password and profile data and saves it in our system",
                       summary="User registration in the system"
                       )
)
class UserRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


@extend_schema_view(
    retrieve=extend_schema(description="Route for viewing your own information",
                           summary="Get authorized user data"),
    update=extend_schema(description="Route for updating your profile information",
                         summary="Update authorized user data"),
    destroy=extend_schema(description="Route for deletion of your own account from system",
                          summary="delete authorized user")
)
class UserMeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.filter(
            id=self.request.user.id
        ).select_related(
            "profile"
        ).prefetch_related(
            "application_set"
        ).annotate(
            vps_count=Count("vps"),
            workload=Case(
                When(vps_count__range=[1, 3], then=Value("EASY", output_field=CharField())),
                When(vps_count__range=[3, 8], then=Value("MEDIUM", output_field=CharField())),
                When(vps_count__gte=9, then=Value("HARD", output_field=CharField())),
                default=Value("VERY_EASY", output_field=CharField())
            ),
            applications_deployed=Count("application", distinct=True)
        ).first()


@extend_schema_view(
    list=extend_schema(description="Route for viewing all users who have been registered in the system",
                       summary="View all users"),
    retrieve=extend_schema(description="Route for viewing specific users, via user id,  "
                                       "who have been registered in the system",
                           summary="View specific user")
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.select_related("profile").prefetch_related("application_set").annotate(
            vps_count=Count("vps"),
            workload=Case(
                When(vps_count__range=[1, 3], then=Value("EASY", output_field=CharField())),
                When(vps_count__range=[3, 8], then=Value("MEDIUM", output_field=CharField())),
                When(vps_count__gte=9, then=Value("HARD", output_field=CharField())),
                default=Value("VERY_EASY", output_field=CharField())
            ),
            applications_deployed=Count("application", distinct=True)
        )


@extend_schema_view(
    put=extend_schema(description="This route is only for changing authorized user email and password",
                      summary="Authorized user credentials update")
)
class UserCredentialsUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCredentialsUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user

@extend_schema_view(
    list=extend_schema(description="Route for obtaining a list of opponents of a user authorized in the system",
                       summary="Get all user contacts"),
    retrieve=extend_schema(description="Route to get a specific contact by its id",
                           summary="Get a contact"),
    create=extend_schema(description="Route to add one user to the contact list",
                         summary="Adding a contact"),
    update=extend_schema(description="Route to change the status of a contact (favorite or not) by its id",
                         summary="Changing the status of a contact"),
    destroy=extend_schema(description="Route to remove a user from the contact list by his id",
                          summary="Deleting a contact")
)
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    pagination_class = DynamicPageNumberPagination
    search_fields = [
        'contact__profile__last_name', 'contact__profile__first_name',
        'contact__profile__middle_name', 'contact__profile__phone', 'contact__email']

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id).select_related(
            'user', 'user__profile', 'user__profile__image',
            'contact', 'contact__profile', 'contact__profile__image'
        ).order_by(
            '-favorite', '-invitation_counter', 'contact__profile__last_name',
            'contact__profile__first_name', 'contact__profile__middle_name', 'id')

    def get_serializer_class(self):
        if not self.kwargs.get('pk') and self.request.method == 'GET':
            return ContactSerializerShort
        return self.serializer_class


@extend_schema_view(
    post=extend_schema(description="Route for uploading a bunch of users (by their phone number) "
                                   "to the authorized user's contact list",
                       summary="Download a pack of contacts")
)
class ContactBulkCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactBulkCreateSerializer
