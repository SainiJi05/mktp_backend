from rest_framework import serializers

from apps.wishlist.models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(source="product.name", read_only=True)
	variant_name = serializers.CharField(source="variant.name", read_only=True)

	class Meta:
		model = WishlistItem
		fields = ["id", "product", "product_name", "variant", "variant_name", "created_at"]
		read_only_fields = ["id", "created_at"]
