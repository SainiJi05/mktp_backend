from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.wallet.views import WalletMeView, WalletTransactionViewSet, WithdrawalRequestViewSet

router = DefaultRouter()
router.register("transactions", WalletTransactionViewSet, basename="wallet-transactions")
router.register("withdrawals", WithdrawalRequestViewSet, basename="wallet-withdrawals")

urlpatterns = [
    path("me/", WalletMeView.as_view(), name="wallet-me"),
    path("", include(router.urls)),
]
