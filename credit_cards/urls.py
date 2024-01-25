from rest_framework.routers import DefaultRouter

from credit_cards import views

router = DefaultRouter()
router.register(prefix="", viewset=views.CreditCardViewSet)

urlpatterns = router.urls
