from django.urls import path

from users import views

urlpatterns = [
    path("", views.UserViewSet.as_view({
        "get": "list",
    })),
    path("me", views.UserMeViewSet.as_view({
        "get": "retrieve",
        "put": "update",
        "delete": "destroy"
    })),
    path("<int:pk>", views.UserViewSet.as_view({
        "get": "retrieve",
    })),
    path("auth", views.UserAuthView.as_view()),
    path("register", views.UserRegisterView.as_view()),
    path("change_credentials", views.UserCredentialsUpdateView.as_view())
]