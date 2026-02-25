from rest_framework import serializers
from apps.common.models import Carousel, Section, SectionProduct, MarketplaceProduct
from apps.catalog.serializers import ProductSerializer


class CarouselSerializer(serializers.ModelSerializer):
	class Meta:
		model = Carousel
		fields = ["id", "image", "title", "description", "redirect_url", "is_active", "order", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class SectionProductSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(
		queryset=__import__('apps.catalog.models', fromlist=['Product']).Product.objects.all(),
		write_only=True,
		source='product'
	)

	class Meta:
		model = SectionProduct
		fields = ["id", "product", "product_id", "order", "created_at"]
		read_only_fields = ["id", "created_at"]


class SectionSerializer(serializers.ModelSerializer):
	products = SectionProductSerializer(many=True, read_only=True)

	class Meta:
		model = Section
		fields = ["id", "name", "description", "section_type", "is_active", "order", "products", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class MarketplaceProductSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	product_id = serializers.PrimaryKeyRelatedField(
		queryset=__import__('apps.catalog.models', fromlist=['Product']).Product.objects.all(),
		write_only=True,
		source='product'
	)

	class Meta:
		model = MarketplaceProduct
		fields = ["id", "product", "product_id", "placement_name", "display_text", "is_featured", "is_active", "order", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]
