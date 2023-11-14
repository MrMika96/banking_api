from django.urls import path
from rest_framework.routers import DefaultRouter

from credit_cards import views

router = DefaultRouter()
router.register(prefix='',
                viewset=views.CreditCardViewSet)

urlpatterns = [
    *router.get_urls(),
    path('create', views.CreateCreditCardViewSet.as_view()),
    path('change_currency/<int:pk>', views.ChangeCardCurrencyView.as_view()),
    path('balance_replenishment/<int:pk>', views.CardBalanceReplenishmentView.as_view()),
    path('money_transfer', views.TransferFromCardToCardView.as_view())
]
