from django.urls import path
from rest_framework.routers import DefaultRouter

from users import views

router = DefaultRouter()
router.register(prefix="", viewset=views.UserViewSet)
router.register(prefix="contacts", viewset=views.ContactViewSet)

urlpatterns = [
    *router.get_urls(),
    path(
        "me",
        views.UserMeViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
    ),
    path("auth", views.UserAuthView.as_view()),
    path("change_credentials", views.UserCredentialsUpdateView.as_view()),
]
