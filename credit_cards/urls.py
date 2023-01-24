from django.urls import path

from credit_cards import views

urlpatterns = [
    path('', views.CreditCardViewSet.as_view({"get": "list", "post": "create"})),
    path('<int:pk>', views.CreditCardViewSet.as_view({"get": "retrieve", "delete": "destroy"})),
    path('create', views.CreateCreditCardViewSet.as_view())
]
