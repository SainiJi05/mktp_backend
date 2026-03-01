from django.contrib import admin
from apps.common.models import Carousel, Section, SectionProduct, MarketplaceProduct


class SectionProductInline(admin.TabularInline):
	model = SectionProduct
	extra = 0
	autocomplete_fields = ['product']


@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "is_active", "order", "created_at")
	list_filter = ("is_active", "created_at")
	search_fields = ("title", "description")
	ordering = ("order", "-created_at")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "section_type", "is_active", "order", "created_at")
	list_filter = ("section_type", "is_active", "created_at")
	search_fields = ("name", "description", "section_type")
	ordering = ("order", "-created_at")
	inlines = [SectionProductInline]


@admin.register(SectionProduct)
class SectionProductAdmin(admin.ModelAdmin):
	list_display = ("id", "section", "product", "order", "created_at")
	list_filter = ("section", "created_at")
	search_fields = ("section__name", "product__name")
	ordering = ("section", "order", "-created_at")
	autocomplete_fields = ['product']


@admin.register(MarketplaceProduct)
class MarketplaceProductAdmin(admin.ModelAdmin):
	list_display = ("id", "product", "placement_name", "is_featured", "is_active", "order", "created_at")
	list_filter = ("placement_name", "is_featured", "is_active", "created_at")
	search_fields = ("product__name", "placement_name", "display_text")
	ordering = ("order", "-created_at")
	autocomplete_fields = ['product']