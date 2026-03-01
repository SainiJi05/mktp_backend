from rest_framework import serializers

from apps.orders.models import CustomizationRequest, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(source="product.name", read_only=True)
	variant_name = serializers.CharField(source="variant.name", read_only=True)

	class Meta:
		model = OrderItem
		fields = [
			"id",
			"product",
			"product_name",
			"variant",
			"variant_name",
			"quantity",
			"price_snapshot",
			"line_total",
		]
		read_only_fields = ["id", "price_snapshot", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True)

	class Meta:
		model = Order
		fields = [
			"id",
			"customer",
			"seller",
			"status",
			"payment_status",
			"razorpay_order_id",
			"razorpay_payment_id",
			"subtotal",
			"shipping_fee",
			"total",
			"seller_settlement_credited",
			"seller_settlement_amount",
			"currency",
			"customer_note",
			"shipping_name",
			"shipping_phone",
			"shipping_line1",
			"shipping_line2",
			"shipping_city",
			"shipping_state",
			"shipping_postal_code",
			"shipping_country",
			"created_at",
			"updated_at",
			"items",
		]
		read_only_fields = [
			"id",
			"customer",
			"seller",
			"status",
			"payment_status",
			"razorpay_order_id",
			"razorpay_payment_id",
			"subtotal",
			"total",
			"seller_settlement_credited",
			"seller_settlement_amount",
			"created_at",
			"updated_at",
		]


class CustomizationRequestSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(source="product.name", read_only=True)
	seller_email = serializers.CharField(source="seller.email", read_only=True)

	class Meta:
		model = CustomizationRequest
		fields = [
			"id",
			"product",
			"product_name",
			"seller",
			"seller_email",
			"customer",
			"status",
			"request_text",
			"quote_price",
			"quote_notes",
			"quoted_by",
			"accepted_at",
			"order",
			"created_at",
			"updated_at",
		]
		read_only_fields = [
			"id",
			"status",
			"customer",
			"seller",
			"quoted_by",
			"accepted_at",
			"order",
			"created_at",
			"updated_at",
		]
