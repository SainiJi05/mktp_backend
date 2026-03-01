from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from apps.orders.models import CustomizationRequest, Order, OrderItem
from apps.orders.serializers import CustomizationRequestSerializer, OrderSerializer
from apps.wallet.services import credit_seller_on_order_delivery


class OrderViewSet(viewsets.ModelViewSet):
	serializer_class = OrderSerializer

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return Order.objects.none()
		user = self.request.user
		if not user.is_authenticated:
			return Order.objects.none()
		if user.is_authenticated and user.role == User.Role.ADMIN:
			return Order.objects.all().prefetch_related("items")
		return Order.objects.filter(Q(customer=user) | Q(seller=user)).prefetch_related("items")

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.IsAuthenticated()]
		if self.action in {"create"}:
			return [permissions.IsAuthenticated()]
		if self.action in {"update", "partial_update", "destroy"}:
			return [IsAdmin()]
		if self.action in {"update_status"}:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated()]

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		items_data = serializer.validated_data.pop("items", [])
		if not items_data:
			raise ValidationError("Order must include at least one item.")

		seller = None
		subtotal = 0
		order_items = []
		for item in items_data:
			product = item["product"]
			variant = item.get("variant")
			if variant and variant.product_id != product.id:
				raise ValidationError("Variant does not belong to the selected product.")
			if seller is None:
				seller = product.seller
			if product.seller_id != seller.id:
				raise ValidationError("All items must be from the same seller.")
			unit_price = variant.price_override if variant and variant.price_override else product.selling_price
			line_total = unit_price * item["quantity"]
			subtotal += line_total
			order_items.append((product, variant, item["quantity"], unit_price, line_total))

		order = Order.objects.create(
			customer=request.user,
			seller=seller,
			subtotal=subtotal,
			total=subtotal + serializer.validated_data.get("shipping_fee", 0),
			**serializer.validated_data,
		)
		for product, variant, quantity, price_snapshot, line_total in order_items:
			OrderItem.objects.create(
				order=order,
				product=product,
				variant=variant,
				quantity=quantity,
				price_snapshot=price_snapshot,
				line_total=line_total,
			)
		return Response(OrderSerializer(order).data, status=201)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	@transaction.atomic
	def update_status(self, request, pk=None):
		order = self.get_object()
		if request.user.role != User.Role.ADMIN and order.seller_id != request.user.id:
			raise PermissionDenied("You can only update your own sales.")
		new_status = request.data.get("status")
		if new_status not in Order.Status.values:
			raise ValidationError("Invalid status.")
		was_delivered = order.status == Order.Status.DELIVERED
		if new_status == Order.Status.DELIVERED and order.payment_status != Order.PaymentStatus.PAID:
			raise ValidationError("Cannot mark unpaid order as delivered.")
		order.status = new_status
		order.save(update_fields=["status", "updated_at"])
		if new_status == Order.Status.DELIVERED and not was_delivered:
			credit_seller_on_order_delivery(order)
		return Response(OrderSerializer(order).data)


class CustomizationRequestViewSet(viewsets.ModelViewSet):
	serializer_class = CustomizationRequestSerializer

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return CustomizationRequest.objects.none()
		user = self.request.user
		if not user.is_authenticated:
			return CustomizationRequest.objects.none()
		if user.is_authenticated and user.role == User.Role.ADMIN:
			return CustomizationRequest.objects.all()
		return CustomizationRequest.objects.filter(Q(customer=user) | Q(seller=user))

	def get_permissions(self):
		if self.action in {"create"}:
			return [permissions.IsAuthenticated()]
		if self.action in {"quote", "list", "retrieve"}:
			return [permissions.IsAuthenticated()]
		if self.action in {"accept"}:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated()]

	def perform_create(self, serializer):
		product = serializer.validated_data["product"]
		serializer.save(customer=self.request.user, seller=product.seller)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def quote(self, request, pk=None):
		custom = self.get_object()
		if custom.seller_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only quote your own requests.")
		quote_price = request.data.get("quote_price")
		if quote_price is None:
			raise ValidationError("quote_price is required.")
		custom.quote_price = quote_price
		custom.quote_notes = request.data.get("quote_notes", "")
		custom.quoted_by = request.user
		custom.status = CustomizationRequest.Status.QUOTED
		custom.save(update_fields=["quote_price", "quote_notes", "quoted_by", "status", "updated_at"])
		return Response(CustomizationRequestSerializer(custom).data)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	@transaction.atomic
	def accept(self, request, pk=None):
		custom = self.get_object()
		if custom.customer_id != request.user.id:
			raise PermissionDenied("You can only accept your own custom requests.")
		if custom.status != CustomizationRequest.Status.QUOTED:
			raise ValidationError("Customization request is not quoted yet.")

		shipping_fields = [
			"shipping_name",
			"shipping_phone",
			"shipping_line1",
			"shipping_line2",
			"shipping_city",
			"shipping_state",
			"shipping_postal_code",
			"shipping_country",
		]
		shipping_data = {field: request.data.get(field, "") for field in shipping_fields}
		if not all(shipping_data[field] for field in shipping_fields if field != "shipping_line2"):
			raise ValidationError("Complete shipping address is required.")

		order = Order.objects.create(
			customer=request.user,
			seller=custom.seller,
			subtotal=custom.quote_price,
			total=custom.quote_price,
			shipping_fee=0,
			**shipping_data,
		)
		OrderItem.objects.create(
			order=order,
			product=custom.product,
			variant=None,
			quantity=1,
			price_snapshot=custom.quote_price,
			line_total=custom.quote_price,
		)
		custom.status = CustomizationRequest.Status.ACCEPTED
		custom.accepted_at = timezone.now()
		custom.order = order
		custom.save(update_fields=["status", "accepted_at", "order", "updated_at"])
		return Response(CustomizationRequestSerializer(custom).data)
