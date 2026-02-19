from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import Address, User


class Category(models.Model):
	name = models.CharField(max_length=150)
	slug = models.SlugField(unique=True)
	image = models.ImageField(upload_to="categories/", null=True, blank=True)
	parent = models.ForeignKey(
		"self", on_delete=models.SET_NULL, related_name="children", null=True, blank=True
	)

	class Meta:
		verbose_name_plural = "categories"

	def __str__(self) -> str:
		return self.name


class ProductColor(models.Model):
	"""Color model with hex code representation"""
	name = models.CharField(max_length=50)
	hex_code = models.CharField(max_length=7, unique=True)  # e.g., #FF5733
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "product colors"

	def __str__(self) -> str:
		return f"{self.name} ({self.hex_code})"


class ProductSize(models.Model):
	"""Size model for products"""
	class SizeChoice(models.TextChoices):
		XS = "xs", "XS"
		S = "s", "S"
		M = "m", "M"
		L = "l", "L"
		XL = "xl", "XL"
		XXL = "xxl", "XXL"
		ONESIZE = "onesize", "One Size"

	size = models.CharField(max_length=10, choices=SizeChoice.choices)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("size",)

	def __str__(self) -> str:
		return self.get_size_display()


class Product(models.Model):
	class ProductType(models.TextChoices):
		NEW = "new", "New"
		USED = "used", "Used"
		RENTAL = "rental", "Rental"

	class Condition(models.TextChoices):
		NEW = "new", "New"
		GENTLY_USED = "gently_used", "Gently Used"
		WORN_3_4 = "worn_3_4", "3-4 Times Worn"
		FAIR = "fair", "Fair"

	class Status(models.TextChoices):
		DRAFT = "draft", "Draft"
		PUBLISHED = "published", "Published"
		ARCHIVED = "archived", "Archived"

	class ShippingOption(models.TextChoices):
		PICKUP = "pickup", "Pickup"
		SELF_SHIPPING = "self_shipping", "Self Shipping"
		BOTH = "both", "Both"

	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	product_type = models.CharField(
		max_length=20, choices=ProductType.choices, default=ProductType.NEW
	)
	original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	selling_price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=3, default="INR")
	condition = models.CharField(
		max_length=20, choices=Condition.choices, default=Condition.NEW
	)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
	shipping_option = models.CharField(
		max_length=20, choices=ShippingOption.choices, default=ShippingOption.BOTH
	)
	pickup_address = models.ForeignKey(
		Address,
		on_delete=models.SET_NULL,
		related_name="pickup_products",
		null=True,
		blank=True,
	)

	# Rental specific fields
	rental_price_per_day = models.DecimalField(
		max_digits=10, decimal_places=2, null=True, blank=True
	)
	late_return_penalty = models.DecimalField(
		max_digits=10, decimal_places=2, default=0, help_text="Penalty per day for late return"
	)
	damage_protection_fee = models.DecimalField(
		max_digits=10, decimal_places=2, default=0, help_text="One-time damage protection fee"
	)

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


class ProductVariant(models.Model):
	"""Product variant combining color and size with specific quantity"""
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
	color = models.ForeignKey(ProductColor, on_delete=models.SET_NULL, null=True, blank=True)
	size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
	sku = models.CharField(max_length=64, unique=True)
	quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
	price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (("product", "color", "size"),)
		ordering = ["color", "size"]

	def __str__(self) -> str:
		color_str = self.color.name if self.color else "No Color"
		size_str = self.size.get_size_display() if self.size else "No Size"
		return f"{self.product.name} - {color_str}/{size_str}"

	def save(self, *args, **kwargs):
		if not self.sku:
			color_code = self.color.hex_code[1:] if self.color else "NC"
			size_code = self.size.size.upper() if self.size else "ONESIZE"
			self.sku = f"{self.product.base_sku}-{color_code}-{size_code}".replace("#", "")
		super().save(*args, **kwargs)


class ProductImage(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
	image = models.ImageField(upload_to="products/")
	alt_text = models.CharField(max_length=150, blank=True)
	sort_order = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["sort_order", "id"]

	def __str__(self) -> str:
		return f"Image {self.id} for {self.product_id}"


class RentalAvailability(models.Model):
	"""Manages rental availability calendar for rental products"""
	product = models.OneToOneField(
		Product, on_delete=models.CASCADE, related_name="rental_availability"
	)
	is_available_from = models.DateField(null=True, blank=True)
	is_available_to = models.DateField(null=True, blank=True)
	blocked_dates = models.JSONField(default=list, blank=True, help_text="List of blocked dates")
	min_rental_days = models.PositiveIntegerField(default=1)
	max_rental_days = models.PositiveIntegerField(default=365)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name_plural = "rental availabilities"

	def __str__(self) -> str:
		return f"Rental Availability for {self.product.name}"
