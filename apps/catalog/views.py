from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from apps.admin_api.models import MarketplaceSettings
from apps.catalog.models import Category, Product
from apps.catalog.serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.AllowAny()]
		return [IsAdmin()]


class ProductViewSet(viewsets.ModelViewSet):
	serializer_class = ProductSerializer
	search_fields = ["name", "description", "base_sku"]
	ordering_fields = ["created_at", "base_price"]
	filterset_fields = ["condition", "status", "seller", "category"]

	def get_queryset(self):
		queryset = Product.objects.select_related("seller", "category")
		if getattr(self, "swagger_fake_view", False):
			return queryset.none()
		user = self.request.user
		if user.is_authenticated and user.role == User.Role.ADMIN:
			return queryset
		if self.action in {"update", "partial_update", "destroy"}:
			if user.is_authenticated:
				return queryset.filter(seller=user)
			return queryset.none()
		if user.is_authenticated:
			return queryset.filter(Q(status=Product.Status.PUBLISHED, is_active=True) | Q(seller=user))
		return queryset.filter(status=Product.Status.PUBLISHED, is_active=True)

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.AllowAny()]
		if self.action in {"create", "update", "partial_update", "destroy"}:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated()]

	def perform_create(self, serializer):
		settings = MarketplaceSettings.get_settings()
		status = Product.Status.PUBLISHED if settings.auto_approve_products else Product.Status.DRAFT
		serializer.save(status=status, seller=self.request.user)

	def perform_update(self, serializer):
		product = self.get_object()
		if self.request.user.role != User.Role.ADMIN and product.seller_id != self.request.user.id:
			raise PermissionDenied("You can only update your own products.")
		serializer.save()
