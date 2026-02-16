from django.db import models

from apps.accounts.models import User
from apps.catalog.models import Product, ProductVariant


class Order(models.Model):
	class Status(models.TextChoices):
		PLACED = "placed", "Placed"
		CONFIRMED = "confirmed", "Confirmed"
		SHIPPED = "shipped", "Shipped"
		DELIVERED = "delivered", "Delivered"
		CANCELED = "canceled", "Canceled"
		REFUNDED = "refunded", "Refunded"

	class PaymentStatus(models.TextChoices):
		UNPAID = "unpaid", "Unpaid"
		PAID = "paid", "Paid"
		FAILED = "failed", "Failed"
		REFUNDED = "refunded", "Refunded"

	customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)
	payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	currency = models.CharField(max_length=3, default="INR")
	customer_note = models.TextField(blank=True)
	shipping_name = models.CharField(max_length=150)
	shipping_phone = models.CharField(max_length=20)
	shipping_line1 = models.CharField(max_length=255)
	shipping_line2 = models.CharField(max_length=255, blank=True)
	shipping_city = models.CharField(max_length=120)
	shipping_state = models.CharField(max_length=120)
	shipping_postal_code = models.CharField(max_length=20)
	shipping_country = models.CharField(max_length=120, default="India")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"Order {self.id}"


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
	quantity = models.PositiveIntegerField(default=1)
	price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
	line_total = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self) -> str:
		return f"{self.product_id} x {self.quantity}"


class CustomizationRequest(models.Model):
	class Status(models.TextChoices):
		REQUESTED = "requested", "Requested"
		QUOTED = "quoted", "Quoted"
		ACCEPTED = "accepted", "Accepted"
		DECLINED = "declined", "Declined"
		CANCELED = "canceled", "Canceled"

	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="custom_requests")
	seller = models.ForeignKey(
		User, on_delete=models.CASCADE, related_name="received_custom_requests"
	)
	customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="custom_requests")
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
	request_text = models.TextField()
	quote_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	quote_notes = models.TextField(blank=True)
	quoted_by = models.ForeignKey(
		User, on_delete=models.SET_NULL, null=True, blank=True, related_name="quotes"
	)
	accepted_at = models.DateTimeField(null=True, blank=True)
	order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"Customization {self.id}"
