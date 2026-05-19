"""Routes module for credit cards."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from credit_cards import views

router = DefaultRouter()
router.register(
    prefix="",
    viewset=views.CreditCardViewSet,
    basename="credit-card"
)

urlpatterns = [
    path("money_transfer/", views.CreditCardMoneyTransferView.as_view()),
    path(
        "change_currency/<int:pk>/",
        views.CreditCardChangeCurrencyView.as_view()
    ),
    path(
        "balance_replenishment/<int:pk>/",
        views.CreditCardBalanceReplenishmentView.as_view()
    ),
    *router.urls
]
