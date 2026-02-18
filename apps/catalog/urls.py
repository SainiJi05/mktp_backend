from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalog.views import (
	CategoryViewSet,
	ProductColorViewSet,
	ProductSizeViewSet,
	ProductViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("colors", ProductColorViewSet, basename="color")
router.register("sizes", ProductSizeViewSet, basename="size")
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
