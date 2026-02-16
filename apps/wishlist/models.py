from django.db import models

from apps.accounts.models import User
from apps.catalog.models import Product, ProductVariant


class WishlistItem(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "product", "variant")

	def __str__(self) -> str:
		return f"Wishlist {self.user_id} -> {self.product_id}"
