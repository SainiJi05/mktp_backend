from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.admin_api.views import (
    MarketplaceSettingsView,
    OrderAdminViewSet,
    ProductModerationViewSet,
    ReportsView,
    UserAdminViewSet,
)

router = DefaultRouter()
router.register("users", UserAdminViewSet, basename="admin-users")
router.register("products", ProductModerationViewSet, basename="admin-products")
router.register("orders", OrderAdminViewSet, basename="admin-orders")

urlpatterns = [
    path("", include(router.urls)),
    path("settings/", MarketplaceSettingsView.as_view(), name="admin-settings"),
    path("reports/", ReportsView.as_view(), name="admin-reports"),
]
