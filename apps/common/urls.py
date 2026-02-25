from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.common.views import CarouselViewSet, SectionViewSet, MarketplaceProductViewSet

router = DefaultRouter()
router.register(r"carousels", CarouselViewSet, basename="carousel")
router.register(r"sections", SectionViewSet, basename="section")
router.register(r"marketplace-products", MarketplaceProductViewSet, basename="marketplace-product")

urlpatterns = [
	path("", include(router.urls)),
]
