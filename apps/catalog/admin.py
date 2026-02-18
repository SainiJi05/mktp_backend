from django.contrib import admin

from apps.catalog.models import (
	Category,
	Product,
	ProductColor,
	ProductImage,
	ProductSize,
	ProductVariant,
	RentalAvailability,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "slug", "parent")
	search_fields = ("name", "slug")


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "hex_code")
	search_fields = ("name", "hex_code")


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
	list_display = ("id", "size")
	search_fields = ("size",)


class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 0


class ProductVariantInline(admin.TabularInline):
	model = ProductVariant
	extra = 0


class RentalAvailabilityInline(admin.TabularInline):
	model = RentalAvailability
	extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "seller", "status", "product_type", "selling_price", "is_active", "created_at")
	list_filter = ("status", "is_active", "condition", "product_type")
	search_fields = ("name", "base_sku", "seller__email")
	inlines = [ProductImageInline, ProductVariantInline, RentalAvailabilityInline]
	ordering = ("-created_at",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ("id", "product", "sort_order")
	list_filter = ("sort_order",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
	list_display = ("id", "product", "color", "size", "sku", "quantity", "is_active")
	list_filter = ("is_active",)
	search_fields = ("sku", "product__name")


@admin.register(RentalAvailability)
class RentalAvailabilityAdmin(admin.ModelAdmin):
	list_display = ("id", "product", "is_available_from", "is_available_to", "min_rental_days", "max_rental_days")
	list_filter = ("is_available_from", "is_available_to")
	search_fields = ("product__name",)
