from django.db import models

from apps.accounts.models import User


class Category(models.Model):
	name = models.CharField(max_length=150)
	slug = models.SlugField(unique=True)
	parent = models.ForeignKey(
		"self", on_delete=models.SET_NULL, related_name="children", null=True, blank=True
	)

	class Meta:
		verbose_name_plural = "categories"

	def __str__(self) -> str:
		return self.name


class Product(models.Model):
	class Condition(models.TextChoices):
		NEW = "new", "New"
		PRE_OWNED = "pre_owned", "Pre-owned"

	class Status(models.TextChoices):
		DRAFT = "draft", "Draft"
		PUBLISHED = "published", "Published"
		ARCHIVED = "archived", "Archived"

	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	base_price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=3, default="INR")
	condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.NEW)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
	is_customizable = models.BooleanField(default=False)
	has_variants = models.BooleanField(default=False)
	base_sku = models.CharField(max_length=64, blank=True)
	stock_quantity = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return self.name


class ProductImage(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
	image_url = models.URLField()
	alt_text = models.CharField(max_length=150, blank=True)
	sort_order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ["sort_order", "id"]

	def __str__(self) -> str:
		return f"Image {self.id} for {self.product_id}"


class ProductVariant(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
	name = models.CharField(max_length=150)
	sku = models.CharField(max_length=64)
	attributes = models.JSONField(default=dict, blank=True)
	price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	stock_quantity = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)

	class Meta:
		unique_together = ("product", "sku")

	def __str__(self) -> str:
		return f"{self.product.name} - {self.name}"
