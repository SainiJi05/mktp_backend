from django.contrib import admin

from apps.wallet.models import Wallet, WalletTransaction, WithdrawalRequest


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance", "updated_at")
    search_fields = ("user__email",)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "transaction_type",
        "source",
        "amount",
        "balance_after",
        "created_at",
    )
    list_filter = ("transaction_type", "source")
    search_fields = ("wallet__user__email", "order__id", "withdrawal_request__id")


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "seller", "amount", "status", "created_at", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("seller__email",)
