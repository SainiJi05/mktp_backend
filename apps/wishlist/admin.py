from django.contrib import admin

from apps.wishlist.models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "variant", "created_at")
    search_fields = ("user__email", "product__name", "variant__name")
