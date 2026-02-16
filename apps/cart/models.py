from django.db import models

from apps.accounts.models import User
from apps.catalog.models import Product, ProductVariant


class Cart(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"Cart {self.user_id}"


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
	quantity = models.PositiveIntegerField(default=1)
	price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("cart", "product", "variant")

	def __str__(self) -> str:
		return f"{self.product_id} x {self.quantity}"
