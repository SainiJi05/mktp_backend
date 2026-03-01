from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from apps.wallet.models import WalletTransaction, WithdrawalRequest
from apps.wallet.serializers import (
    WalletSerializer,
    WalletTransactionSerializer,
    WithdrawalRequestSerializer,
)
from apps.wallet.services import get_or_create_wallet


class WalletMeView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet = get_or_create_wallet(self.request.user)
        wallet.transactions.all()[:20]
        return wallet


class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return WalletTransaction.objects.none()
        if user.role == User.Role.ADMIN:
            return WalletTransaction.objects.select_related("wallet", "order", "withdrawal_request")
        return WalletTransaction.objects.filter(wallet__user=user).select_related(
            "wallet", "order", "withdrawal_request"
        )


class WithdrawalRequestViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return WithdrawalRequest.objects.none()
        queryset = WithdrawalRequest.objects.select_related("seller", "wallet", "bank_details", "reviewed_by")
        if user.role == User.Role.ADMIN:
            return queryset
        return queryset.filter(seller=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Role.CUSTOMER:
            raise PermissionDenied("Only sellers can create withdrawal requests.")

        bank_details = getattr(user, "bank_details", None)
        if bank_details is None:
            raise ValidationError({"bank_details": "Please add bank details before requesting withdrawal."})

        wallet = get_or_create_wallet(user)
        amount = Decimal(serializer.validated_data["amount"])
        if amount > wallet.balance:
            raise ValidationError({"amount": "Insufficient wallet balance."})

        serializer.save(
            seller=user,
            wallet=wallet,
            bank_details=bank_details,
            account_holder_name_snapshot=bank_details.account_holder_name,
            account_number_snapshot=bank_details.account_number,
            ifsc_code_snapshot=bank_details.ifsc_code,
            upi_id_snapshot=bank_details.upi_id,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    @transaction.atomic
    def approve(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != WithdrawalRequest.Status.PENDING:
            raise ValidationError("Only pending withdrawal requests can be approved.")

        wallet = withdrawal.wallet
        wallet = wallet.__class__.objects.select_for_update().get(pk=wallet.pk)
        amount = Decimal(withdrawal.amount)
        if amount > wallet.balance:
            raise ValidationError("Insufficient wallet balance for this approval.")

        wallet.balance = wallet.balance - amount
        wallet.save(update_fields=["balance", "updated_at"])

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=WalletTransaction.TransactionType.DEBIT,
            source=WalletTransaction.Source.WITHDRAWAL,
            amount=amount,
            balance_after=wallet.balance,
            withdrawal_request=withdrawal,
            description=f"Withdrawal approved for request #{withdrawal.id}",
            meta={
                "approved_by": request.user.id,
                "bank_details_id": withdrawal.bank_details_id,
            },
        )

        withdrawal.status = WithdrawalRequest.Status.APPROVED
        withdrawal.reviewed_by = request.user
        withdrawal.reviewed_at = timezone.now()
        withdrawal.admin_note = request.data.get("admin_note", "")
        withdrawal.save(update_fields=["status", "reviewed_by", "reviewed_at", "admin_note", "updated_at"])

        return Response(self.get_serializer(withdrawal).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != WithdrawalRequest.Status.PENDING:
            raise ValidationError("Only pending withdrawal requests can be rejected.")

        withdrawal.status = WithdrawalRequest.Status.REJECTED
        withdrawal.reviewed_by = request.user
        withdrawal.reviewed_at = timezone.now()
        withdrawal.admin_note = request.data.get("admin_note", "")
        withdrawal.save(update_fields=["status", "reviewed_by", "reviewed_at", "admin_note", "updated_at"])

        return Response(self.get_serializer(withdrawal).data)
