from django.urls import path

from banks import views

urlpatterns = [
    path('', views.BanksViewSet.as_view({"get": "list", "post": "create"})),
    path('<int:pk>', views.BanksViewSet.as_view({"get": "retrieve", "put": "update"})),
]