from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.integrations.views import MakePaymentView, VerifyPaymentView, VTONTryOnView

router = DefaultRouter()

urlpatterns = [
    path("make-payment/", MakePaymentView.as_view(), name="make-payment"),
    path("verify-payment/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("vton/try-on/", VTONTryOnView.as_view(), name="vton-try-on"),
    path("", include(router.urls)),
]
