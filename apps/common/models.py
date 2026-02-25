from django.db import models
from apps.catalog.models import Product


class Carousel(models.Model):
	"""Carousel items for home page display"""
	image = models.ImageField(upload_to="carousel/")
	title = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	redirect_url = models.URLField(blank=True)
	is_active = models.BooleanField(default=True)
	order = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["order", "-created_at"]

	def __str__(self) -> str:
		return self.title or f"Carousel {self.id}"


class Section(models.Model):
	"""Sections containing products (e.g., Featured Products, Most Sells, New Comers)"""
	name = models.CharField(max_length=255, unique=True)
	description = models.TextField(blank=True)
	section_type = models.CharField(max_length=50)  # e.g., "featured", "most_sells", "new_comers"
	is_active = models.BooleanField(default=True)
	order = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["order", "-created_at"]

	def __str__(self) -> str:
		return self.name


class SectionProduct(models.Model):
	"""Junction model for products in sections"""
	section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="products")
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	order = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("section", "product")
		ordering = ["order", "-created_at"]

	def __str__(self) -> str:
		return f"{self.section.name} - {self.product.name}"


class MarketplaceProduct(models.Model):
	"""Products displayed at special marketplace locations"""
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="marketplace_placements")
	placement_name = models.CharField(max_length=255)  # e.g., "Hot Deals", "Flash Sale"
	display_text = models.TextField(blank=True)
	is_featured = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	order = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["order", "-created_at"]

	def __str__(self) -> str:
		return f"{self.product.name} - {self.placement_name}"
