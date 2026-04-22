"""Routes module for banks."""
from rest_framework.routers import DefaultRouter

from banks import views

router = DefaultRouter()
router.register(prefix="payment_system", viewset=views.PaymentSystemViewSet)
router.register(prefix="", viewset=views.BanksViewSet)


urlpatterns = router.urls
