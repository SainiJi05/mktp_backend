from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.orders.models import Order
from apps.wallet.models import Wallet, WalletTransaction


def _to_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


@transaction.atomic
def credit_seller_on_order_delivery(order: Order):
    if order.seller_settlement_credited:
        return None
    if order.payment_status != Order.PaymentStatus.PAID:
        raise ValidationError("Only paid orders can be settled to seller wallet.")

    commission_percent = Decimal(str(settings.PLATFORM_COMMISSION_PERCENT))
    gross = _to_money(Decimal(order.total))
    commission_amount = _to_money((gross * commission_percent) / Decimal("100"))
    net_amount = _to_money(gross - commission_amount)
    if net_amount < 0:
        net_amount = Decimal("0.00")

    wallet = Wallet.objects.select_for_update().filter(user=order.seller).first()
    if wallet is None:
        wallet = Wallet.objects.create(user=order.seller)

    wallet.balance = _to_money(Decimal(wallet.balance) + net_amount)
    wallet.save(update_fields=["balance", "updated_at"])

    tx = WalletTransaction.objects.create(
        wallet=wallet,
        transaction_type=WalletTransaction.TransactionType.CREDIT,
        source=WalletTransaction.Source.ORDER_SETTLEMENT,
        amount=net_amount,
        balance_after=wallet.balance,
        order=order,
        description=f"Settlement credited for order #{order.id}",
        meta={
            "gross_order_total": str(gross),
            "commission_percent": str(commission_percent),
            "commission_amount": str(commission_amount),
            "net_settlement_amount": str(net_amount),
        },
    )

    order.seller_settlement_credited = True
    order.seller_settlement_amount = net_amount
    order.save(update_fields=["seller_settlement_credited", "seller_settlement_amount", "updated_at"])

    return tx
