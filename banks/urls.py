from rest_framework.routers import DefaultRouter

from banks import views


router = DefaultRouter()
router.register(prefix="", viewset=views.BanksViewSet)
router.register(prefix="payment_system", viewset=views.PaymentSystemViewSet)


urlpatterns = router.urls
