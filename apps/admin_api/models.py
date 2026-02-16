from django.db import models


class MarketplaceSettings(models.Model):
	auto_approve_products = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	@classmethod
	def get_settings(cls) -> "MarketplaceSettings":
		instance = cls.objects.first()
		if instance is None:
			instance = cls.objects.create()
		return instance

	def __str__(self) -> str:
		return "Marketplace Settings"
