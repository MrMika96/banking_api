"""Routes module for users."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from users import views

router = DefaultRouter()
router.register(
    prefix="contacts",
    viewset=views.ContactViewSet,
    basename="contacts"
)
router.register(prefix="", viewset=views.UserViewSet, basename="user")

urlpatterns = [
    path(
        "me/",
        views.UserMeViewSet.as_view(
            {"get": "retrieve", "delete": "destroy"}
        ),
        name="user-data"
    ),
    path(
        "me/profile/",
        views.UserMeProfileView.as_view(),
        name="user-profile-update"
    ),
    path(
        "register/",
        views.UserRegisterView.as_view(),
        name="user-register"
    ),
    path("auth/", views.UserAuthView.as_view(), name="user-auth"),
    path(
        "auth/refresh/",
        views.UserAuthRefreshView.as_view(),
        name="user-refresh"),
    path(
        "change_credentials/",
        views.UserCredentialsUpdateView.as_view(),
        name="user-change-credentials"
    ),
    path(
        "contacts/bulk_create/",
        views.ContactBulkCreateViewSet.as_view(),
        name="user-contacts-bulk-create"
    ),
    *router.get_urls(),
]
