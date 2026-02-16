from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.cart.views import CartItemViewSet, CartView

router = DefaultRouter()
router.register("items", CartItemViewSet, basename="cart-item")

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("", include(router.urls)),
]
