from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.orders.views import CustomizationRequestViewSet, OrderViewSet

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")
router.register("customizations", CustomizationRequestViewSet, basename="customization")

urlpatterns = [
    path("", include(router.urls)),
]
