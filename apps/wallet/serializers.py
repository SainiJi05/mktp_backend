from decimal import Decimal

from rest_framework import serializers

from apps.wallet.models import Wallet, WalletTransaction, WithdrawalRequest


class WalletTransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    withdrawal_request_id = serializers.IntegerField(source="withdrawal_request.id", read_only=True)

    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "transaction_type",
            "source",
            "amount",
            "balance_after",
            "order_id",
            "withdrawal_request_id",
            "description",
            "meta",
            "created_at",
        ]
        read_only_fields = fields


class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "balance", "updated_at", "transactions"]
        read_only_fields = fields


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    bank_details_id = serializers.IntegerField(source="bank_details.id", read_only=True)

    class Meta:
        model = WithdrawalRequest
        fields = [
            "id",
            "seller",
            "wallet",
            "bank_details",
            "bank_details_id",
            "amount",
            "status",
            "account_holder_name_snapshot",
            "account_number_snapshot",
            "ifsc_code_snapshot",
            "upi_id_snapshot",
            "admin_note",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "seller",
            "wallet",
            "status",
            "account_holder_name_snapshot",
            "account_number_snapshot",
            "ifsc_code_snapshot",
            "upi_id_snapshot",
            "admin_note",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value: Decimal):
        if value <= 0:
            raise serializers.ValidationError("amount must be greater than 0")
        return value
