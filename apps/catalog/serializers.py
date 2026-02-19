from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import Address, User
from apps.accounts.serializers import AddressSerializer
from apps.catalog.models import (
	Category,
	Product,
	ProductColor,
	ProductImage,
	ProductSize,
	ProductVariant,
	RentalAvailability,
)


class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ["id", "name", "slug", "image", "parent"]

	def validate(self, attrs):
		if self.instance is None and not attrs.get("image"):
			raise serializers.ValidationError({"image": "Category image is required."})
		return super().validate(attrs)


class ProductColorSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductColor
		fields = ["id", "name", "hex_code"]


class ProductSizeSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductSize
		fields = ["id", "size", "size_display"]

	size_display = serializers.CharField(source="get_size_display", read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
	image_url = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = ProductImage
		fields = ["id", "image", "image_url", "alt_text", "sort_order"]

	def get_image_url(self, obj):
		if obj.image:
			request = self.context.get("request")
			if request:
				return request.build_absolute_uri(obj.image.url)
			return obj.image.url
		return ""


class ProductVariantSerializer(serializers.ModelSerializer):
	color = ProductColorSerializer(read_only=True)
	size = ProductSizeSerializer(read_only=True)
	color_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
	size_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

	class Meta:
		model = ProductVariant
		fields = [
			"id",
			"color",
			"color_id",
			"size",
			"size_id",
			"sku",
			"quantity",
			"price_override",
			"is_active",
		]

	def create(self, validated_data):
		color_id = validated_data.pop("color_id", None)
		size_id = validated_data.pop("size_id", None)
		variant = ProductVariant.objects.create(**validated_data)
		if color_id:
			variant.color_id = color_id
		if size_id:
			variant.size_id = size_id
		variant.save()
		return variant


class RentalAvailabilitySerializer(serializers.ModelSerializer):
	class Meta:
		model = RentalAvailability
		fields = [
			"is_available_from",
			"is_available_to",
			"blocked_dates",
			"min_rental_days",
			"max_rental_days",
		]


class ProductSerializer(serializers.ModelSerializer):
	images = ProductImageSerializer(many=True, required=False)
	variants = ProductVariantSerializer(many=True, required=False)
	rental_availability = RentalAvailabilitySerializer(required=False)
	pickup_address = AddressSerializer(read_only=True)
	pickup_address_id = serializers.PrimaryKeyRelatedField(
		queryset=Address.objects.all(),
		source="pickup_address",
		write_only=True,
		required=False,
		allow_null=True,
	)
	seller_id = serializers.IntegerField(source="seller.id", read_only=True)
	seller_email = serializers.CharField(source="seller.email", read_only=True)

	class Meta:
		model = Product
		fields = [
			"id",
			"seller",
			"seller_id",
			"seller_email",
			"category",
			"name",
			"description",
			"product_type",
			"original_price",
			"selling_price",
			"currency",
			"condition",
			"status",
			"shipping_option",
			"pickup_address",
			"pickup_address_id",
			"rental_price_per_day",
			"late_return_penalty",
			"damage_protection_fee",
			"is_customizable",
			"has_variants",
			"base_sku",
			"stock_quantity",
			"is_active",
			"created_at",
			"updated_at",
			"images",
			"variants",
			"rental_availability",
		]
		read_only_fields = ["id", "seller", "seller_id", "seller_email", "created_at", "updated_at", "has_variants"]

	@transaction.atomic
	def create(self, validated_data):
		images_data = validated_data.pop("images", [])
		variants_data = validated_data.pop("variants", [])
		rental_availability_data = validated_data.pop("rental_availability", None)
		
		product = Product.objects.create(**validated_data)
		
		for image in images_data:
			ProductImage.objects.create(product=product, **image)
		
		for variant in variants_data:
			ProductVariant.objects.create(product=product, **variant)
		
		if variants_data:
			product.has_variants = True
			product.save(update_fields=["has_variants"])
		
		if rental_availability_data and product.product_type == Product.ProductType.RENTAL:
			RentalAvailability.objects.create(product=product, **rental_availability_data)
		
		return product

	def validate(self, attrs):
		pickup_address = attrs.get("pickup_address")
		request = self.context.get("request")
		if pickup_address and request and request.user.is_authenticated:
			if request.user.role != User.Role.ADMIN and pickup_address.user_id != request.user.id:
				raise serializers.ValidationError(
					{"pickup_address_id": "Pickup address must belong to the current user."}
				)
		return super().validate(attrs)

	@transaction.atomic
	def update(self, instance, validated_data):
		images_data = validated_data.pop("images", None)
		variants_data = validated_data.pop("variants", None)
		rental_availability_data = validated_data.pop("rental_availability", None)
		
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
		
		if rental_availability_data is not None:
			if instance.product_type == Product.ProductType.RENTAL:
				rental_avail, created = RentalAvailability.objects.get_or_create(product=instance)
				for attr, value in rental_availability_data.items():
					setattr(rental_avail, attr, value)
				rental_avail.save()
			else:
				RentalAvailability.objects.filter(product=instance).delete()
		
		return instance

