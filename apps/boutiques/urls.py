from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.boutiques.views import BoutiqueViewSet

router = DefaultRouter()
router.register("", BoutiqueViewSet, basename="boutique")

urlpatterns = [
    path("", include(router.urls)),
]
