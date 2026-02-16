from django.db import transaction
from rest_framework import serializers

from apps.catalog.models import Category, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ["id", "name", "slug", "parent"]


class ProductImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductImage
		fields = ["id", "image_url", "alt_text", "sort_order"]


class ProductVariantSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductVariant
		fields = ["id", "name", "sku", "attributes", "price_override", "stock_quantity", "is_active"]


class ProductSerializer(serializers.ModelSerializer):
	images = ProductImageSerializer(many=True, required=False)
	variants = ProductVariantSerializer(many=True, required=False)
	seller_id = serializers.IntegerField(source="seller.id", read_only=True)

	class Meta:
		model = Product
		fields = [
			"id",
			"seller",
			"seller_id",
			"category",
			"name",
			"description",
			"base_price",
			"currency",
			"condition",
			"status",
			"is_customizable",
			"has_variants",
			"base_sku",
			"stock_quantity",
			"is_active",
			"created_at",
			"updated_at",
			"images",
			"variants",
		]
		read_only_fields = ["id", "seller", "seller_id", "created_at", "updated_at", "has_variants"]

	@transaction.atomic
	def create(self, validated_data):
		images_data = validated_data.pop("images", [])
		variants_data = validated_data.pop("variants", [])
		product = Product.objects.create(**validated_data)
		for image in images_data:
			ProductImage.objects.create(product=product, **image)
		for variant in variants_data:
			ProductVariant.objects.create(product=product, **variant)
		if variants_data:
			product.has_variants = True
			product.save(update_fields=["has_variants"])
		return product

	@transaction.atomic
	def update(self, instance, validated_data):
		images_data = validated_data.pop("images", None)
		variants_data = validated_data.pop("variants", None)
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()
		if images_data is not None:
			instance.images.all().delete()
			for image in images_data:
				ProductImage.objects.create(product=instance, **image)
		if variants_data is not None:
			instance.variants.all().delete()
			for variant in variants_data:
				ProductVariant.objects.create(product=instance, **variant)
			instance.has_variants = bool(variants_data)
			instance.save(update_fields=["has_variants"])
		return instance
