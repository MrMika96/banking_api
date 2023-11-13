from django.urls import path
from rest_framework.routers import DefaultRouter

from banks import views


router = DefaultRouter()
router.register(prefix="",
                viewset=views.BanksViewSet
                )


urlpatterns = [
    *router.get_urls(),
    # path('', views.BanksViewSet.as_view({"get": "list", "post": "create"})),
    # path('<int:pk>', views.BanksViewSet.as_view({"get": "retrieve", "put": "update"})),
    path('payment_system', views.PaymentSystemViewSet.as_view({"get": "list", "post": "create"})),
    path('payment_system/<int:pk>', views.PaymentSystemViewSet.as_view({"get": "retrieve", "put": "update"})),
]