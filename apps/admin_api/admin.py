from django.contrib import admin

from apps.admin_api.models import MarketplaceSettings


@admin.register(MarketplaceSettings)
class MarketplaceSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "auto_approve_products", "updated_at")
