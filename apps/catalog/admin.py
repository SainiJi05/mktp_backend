from django.contrib import admin

from apps.catalog.models import Category, Product, ProductImage, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent")
    search_fields = ("name", "slug")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "seller", "status", "base_price", "is_active", "created_at")
    list_filter = ("status", "is_active", "condition")
    search_fields = ("name", "base_sku", "seller__email")
    inlines = [ProductImageInline, ProductVariantInline]
    ordering = ("-created_at",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "sort_order")
    list_filter = ("sort_order",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name", "sku", "stock_quantity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "sku", "product__name")
