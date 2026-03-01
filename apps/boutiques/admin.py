from django.contrib import admin

from apps.boutiques.models import Boutique


@admin.register(Boutique)
class BoutiqueAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "is_active", "created_at")
    list_filter = ("status", "is_active", "created_at")
    search_fields = ("name", "owner__email", "city", "state")
    ordering = ("-created_at",)
    autocomplete_fields = ['owner']
