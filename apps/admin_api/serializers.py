from rest_framework import serializers

from apps.accounts.models import User
from apps.admin_api.models import MarketplaceSettings
from apps.catalog.models import Product
from apps.orders.models import Order


class MarketplaceSettingsSerializer(serializers.ModelSerializer):
	class Meta:
		model = MarketplaceSettings
		fields = ["id", "auto_approve_products", "created_at", "updated_at"]
		read_only_fields = ["id", "created_at", "updated_at"]


class UserAdminSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = [
			"id",
			"email",
			"phone",
			"first_name",
			"last_name",
			"role",
			"is_active",
			"is_verified",
			"date_joined",
		]
		read_only_fields = ["id", "date_joined"]


class ProductModerationSerializer(serializers.ModelSerializer):
	seller_email = serializers.CharField(source="seller.email", read_only=True)

	class Meta:
		model = Product
		fields = [
			"id",
			"name",
			"seller",
			"seller_email",
			"status",
			"is_active",
			"created_at",
		]
		read_only_fields = ["id", "created_at", "seller", "seller_email"]


class OrderAdminSerializer(serializers.ModelSerializer):
	customer_email = serializers.CharField(source="customer.email", read_only=True)
	seller_email = serializers.CharField(source="seller.email", read_only=True)

	class Meta:
		model = Order
		fields = [
			"id",
			"customer",
			"customer_email",
			"seller",
			"seller_email",
			"status",
			"payment_status",
			"subtotal",
			"total",
			"currency",
			"created_at",
		]
		read_only_fields = ["id", "created_at", "customer_email", "seller", "seller_email"]


class ReportsSerializer(serializers.Serializer):
	users_by_role = serializers.ListField(child=serializers.DictField(), read_only=True)
	orders_by_status = serializers.ListField(child=serializers.DictField(), read_only=True)
