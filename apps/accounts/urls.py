from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import AddressViewSet, LoginView, MeView, RegisterView

router = DefaultRouter()
router.register("addresses", AddressViewSet, basename="address")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
]
