from django.db import models

from apps.accounts.models import BankDetails, User


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Wallet<{self.user.email}>"


class WithdrawalRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawal_requests")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="withdrawal_requests")
    bank_details = models.ForeignKey(BankDetails, on_delete=models.PROTECT, related_name="withdrawal_requests")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    account_holder_name_snapshot = models.CharField(max_length=150, blank=True)
    account_number_snapshot = models.CharField(max_length=50, blank=True)
    ifsc_code_snapshot = models.CharField(max_length=20, blank=True)
    upi_id_snapshot = models.CharField(max_length=150, blank=True)
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="withdrawal_requests_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Withdrawal<{self.id}> {self.seller.email} - {self.amount}"


class WalletTransaction(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    class Source(models.TextChoices):
        ORDER_SETTLEMENT = "order_settlement", "Order Settlement"
        WITHDRAWAL = "withdrawal", "Withdrawal"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    source = models.CharField(max_length=30, choices=Source.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallet_transactions",
    )
    withdrawal_request = models.ForeignKey(
        WithdrawalRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallet_transactions",
    )
    description = models.CharField(max_length=255, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.wallet.user.email} {self.transaction_type} {self.amount}"
