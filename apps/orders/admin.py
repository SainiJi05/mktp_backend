from django.contrib import admin

from apps.orders.models import CustomizationRequest, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "seller", "status", "payment_status", "total", "created_at")
    list_filter = ("status", "payment_status")
    search_fields = ("customer__email", "seller__email")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "variant", "quantity", "line_total")
    search_fields = ("order__id", "product__name", "variant__name")


@admin.register(CustomizationRequest)
class CustomizationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "customer", "status", "quote_price", "created_at")
    list_filter = ("status",)
    search_fields = ("product__name", "customer__email", "seller__email")
