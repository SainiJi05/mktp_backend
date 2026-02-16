from django.db import models

from apps.accounts.models import User


class Boutique(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		APPROVED = "approved", "Approved"
		REJECTED = "rejected", "Rejected"

	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boutiques")
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	phone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	address = models.TextField(blank=True)
	city = models.CharField(max_length=120, blank=True)
	state = models.CharField(max_length=120, blank=True)
	country = models.CharField(max_length=120, default="India")
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return self.name
