from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.wishlist.views import WishlistItemViewSet

router = DefaultRouter()
router.register("items", WishlistItemViewSet, basename="wishlist-item")

urlpatterns = [
    path("", include(router.urls)),
]
