from django.db.models import Count
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from apps.admin_api.models import MarketplaceSettings
from apps.admin_api.serializers import (
	MarketplaceSettingsSerializer,
	OrderAdminSerializer,
	ProductModerationSerializer,
	ReportsSerializer,
	UserAdminSerializer,
)
from apps.catalog.models import Product
from apps.orders.models import Order


class MarketplaceSettingsView(generics.RetrieveUpdateAPIView):
	serializer_class = MarketplaceSettingsSerializer
	permission_classes = [IsAdmin]

	def get_object(self):
		return MarketplaceSettings.get_settings()


class UserAdminViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all().order_by("-date_joined")
	serializer_class = UserAdminSerializer
	permission_classes = [IsAdmin]


class ProductModerationViewSet(viewsets.ModelViewSet):
	queryset = Product.objects.all().order_by("-created_at")
	serializer_class = ProductModerationSerializer
	permission_classes = [IsAdmin]

	@action(detail=True, methods=["post"], permission_classes=[IsAdmin])
	def publish(self, request, pk=None):
		product = self.get_object()
		product.status = Product.Status.PUBLISHED
		product.save(update_fields=["status", "updated_at"])
		return Response(self.get_serializer(product).data)

	@action(detail=True, methods=["post"], permission_classes=[IsAdmin])
	def archive(self, request, pk=None):
		product = self.get_object()
		product.status = Product.Status.ARCHIVED
		product.save(update_fields=["status", "updated_at"])
		return Response(self.get_serializer(product).data)


class OrderAdminViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Order.objects.all().order_by("-created_at")
	serializer_class = OrderAdminSerializer
	permission_classes = [IsAdmin]

	@action(detail=True, methods=["post"], permission_classes=[IsAdmin])
	def update_status(self, request, pk=None):
		order = self.get_object()
		new_status = request.data.get("status")
		if new_status not in Order.Status.values:
			return Response({"detail": "Invalid status."}, status=400)
		order.status = new_status
		order.save(update_fields=["status", "updated_at"])
		return Response(self.get_serializer(order).data)


class ReportsView(generics.GenericAPIView):
	serializer_class = ReportsSerializer
	permission_classes = [IsAdmin]

	def get(self, request, *args, **kwargs):
		users_by_role = User.objects.values("role").annotate(count=Count("id"))
		orders_by_status = Order.objects.values("status").annotate(count=Count("id"))
		return Response(
			{
				"users_by_role": list(users_by_role),
				"orders_by_status": list(orders_by_status),
			}
		)
