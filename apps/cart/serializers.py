from rest_framework import serializers

from apps.catalog.models import Product, ProductVariant
from apps.cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(source="product.name", read_only=True)
	variant_name = serializers.CharField(source="variant.name", read_only=True)

	class Meta:
		model = CartItem
		fields = [
			"id",
			"product",
			"product_name",
			"variant",
			"variant_name",
			"quantity",
			"price_snapshot",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "price_snapshot", "created_at", "updated_at"]


class CartSerializer(serializers.ModelSerializer):
	items = CartItemSerializer(many=True, read_only=True)

	class Meta:
		model = Cart
		fields = ["id", "items", "updated_at"]
		read_only_fields = ["id", "updated_at"]


class CartItemAddSerializer(serializers.Serializer):
	product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
	variant = serializers.PrimaryKeyRelatedField(
		queryset=ProductVariant.objects.all(), required=False, allow_null=True
	)
	quantity = serializers.IntegerField(min_value=1, default=1)
