"""Routes module for users."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from users import views

router = DefaultRouter()
router.register(prefix="contacts", viewset=views.ContactViewSet)
router.register(prefix="", viewset=views.UserViewSet)

urlpatterns = [
    path(
        "me/",
        views.UserMeViewSet.as_view(
            {"get": "retrieve", "delete": "destroy"}
        ),
    ),
    path("me/profile/", views.UserMeProfileView.as_view()),
    path("register/", views.UserRegisterView.as_view()),
    path("auth/", views.UserAuthView.as_view()),
    path("auth/refresh/", views.UserAuthRefreshView.as_view()),
    path("change_credentials/", views.UserCredentialsUpdateView.as_view()),
    path("contacts/bulk_create/", views.ContactBulkCreateViewSet.as_view()),
    *router.get_urls(),
]
