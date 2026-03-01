from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
import random

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from apps.admin_api.models import MarketplaceSettings
from apps.catalog.models import (
	Category,
	Product,
	ProductColor,
	ProductImage,
	ProductSize,
	ProductVariant,
	RentalAvailability,
)
from apps.catalog.serializers import (
	CategorySerializer,
	ProductColorSerializer,
	ProductImageSerializer,
	ProductSerializer,
	ProductSizeSerializer,
	ProductVariantSerializer,
	RentalAvailabilitySerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.AllowAny()]
		return [IsAdmin()]


class ProductColorViewSet(viewsets.ModelViewSet):
	"""ViewSet for managing product colors"""
	queryset = ProductColor.objects.all()
	serializer_class = ProductColorSerializer

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.AllowAny()]
		return [IsAdmin()]


class ProductSizeViewSet(viewsets.ModelViewSet):
	"""ViewSet for managing product sizes"""
	queryset = ProductSize.objects.all()
	serializer_class = ProductSizeSerializer

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.AllowAny()]
		return [IsAdmin()]


class ProductViewSet(viewsets.ModelViewSet):
	serializer_class = ProductSerializer
	parser_classes = [MultiPartParser, FormParser, JSONParser]
	search_fields = ["name", "description", "base_sku"]
	ordering_fields = ["created_at", "selling_price"]
	filterset_fields = ["condition", "status", "seller", "category", "product_type"]

	def get_queryset(self):
		queryset = Product.objects.prefetch_related("images", "variants").select_related(
			"seller", "category"
		)
		if getattr(self, "swagger_fake_view", False):
			return queryset.none()
		user = self.request.user
		if user.is_authenticated and user.role == User.Role.ADMIN:
			return queryset
		if self.action in {"update", "partial_update", "destroy"}:
			if user.is_authenticated:
				return queryset.filter(seller=user)
			return queryset.none()
		# if user.is_authenticated:
			# return queryset.filter(Q(status=Product.Status.PUBLISHED) | Q(seller=user))
		return queryset

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.AllowAny()]
		if self.action in {"create", "update", "partial_update", "destroy"}:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated()]

	def perform_create(self, serializer):
		settings = MarketplaceSettings.get_settings()
		status_choice = Product.Status.PUBLISHED if settings.auto_approve_products else Product.Status.DRAFT
		serializer.save(status=status_choice, seller=self.request.user)

	def perform_update(self, serializer):
		product = self.get_object()
		if self.request.user.role != User.Role.ADMIN and product.seller_id != self.request.user.id:
			raise PermissionDenied("You can only update your own products.")
		serializer.save()

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def add_images(self, request, pk=None):
		"""Add images to a product"""
		product = self.get_object()
		if product.seller_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only add images to your own products.")
		
		images_data = request.data.get("images", [])
		serializer = ProductImageSerializer(data=images_data, many=True, context={"request": request})
		if serializer.is_valid():
			for image in serializer.validated_data:
				ProductImage.objects.create(product=product, **image)
			return Response(
				ProductImageSerializer(
					product.images.all(),
					many=True,
					context={"request": request},
				).data
			)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def add_variants(self, request, pk=None):
		"""Add or update variants to a product"""
		product = self.get_object()
		if product.seller_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only add variants to your own products.")
		
		variants_data = request.data.get("variants", [])
		serializer = ProductVariantSerializer(data=variants_data, many=True)
		if serializer.is_valid():
			for variant in serializer.validated_data:
				variant["product"] = product
				ProductVariant.objects.update_or_create(
					product=product,
					color_id=variant.get("color_id"),
					size_id=variant.get("size_id"),
					defaults=variant,
				)
			product.has_variants = True
			product.save(update_fields=["has_variants"])
			return Response(
				ProductVariantSerializer(product.variants.all(), many=True).data,
				status=status.HTTP_201_CREATED,
			)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def set_rental_availability(self, request, pk=None):
		"""Set rental availability for a rental product"""
		product = self.get_object()
		if product.seller_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only update your own products.")
		
		if product.product_type != Product.ProductType.RENTAL:
			raise ValidationError("This product is not a rental product.")
		
		serializer = RentalAvailabilitySerializer(data=request.data)
		if serializer.is_valid():
			rental_avail, created = RentalAvailability.objects.get_or_create(product=product)
			for attr, value in serializer.validated_data.items():
				setattr(rental_avail, attr, value)
			rental_avail.save()
			return Response(RentalAvailabilitySerializer(rental_avail).data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
	def my_products(self, request):
		"""Get all products from the authenticated seller"""
		products = Product.objects.filter(seller=request.user).prefetch_related("images", "variants")
		serializer = self.get_serializer(products, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=["get"])
	def by_seller(self, request):
		"""Get published products by a specific seller"""
		seller_id = request.query_params.get("seller_id")
		if not seller_id:
			return Response(
				{"error": "seller_id parameter is required"},
				status=status.HTTP_400_BAD_REQUEST,
			)
		
		products = Product.objects.filter(
			seller_id=seller_id,
			status=Product.Status.PUBLISHED,
			is_active=True,
		).prefetch_related("images", "variants")
		serializer = self.get_serializer(products, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def publish(self, request, pk=None):
		"""Publish a product"""
		product = self.get_object()
		if product.seller_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only publish your own products.")
		
		product.status = Product.Status.PUBLISHED
		product.save(update_fields=["status"])
		return Response({"status": "Product published successfully"})

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def unpublish(self, request, pk=None):
		"""Unpublish a product"""
		product = self.get_object()
		if product.seller_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only unpublish your own products.")
		
		product.status = Product.Status.DRAFT
		product.save(update_fields=["status"])
		return Response({"status": "Product unpublished successfully"})

	@action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
	def all(self, request):
		"""Get all products with optional filters"""
		queryset = self.get_queryset()

		# Apply filters
		name = request.query_params.get("name")
		if name:
			queryset = queryset.filter(name__icontains=name)

		category_id = request.query_params.get("category")
		if category_id:
			queryset = queryset.filter(category_id=category_id)

		color_id = request.query_params.get("color")
		if color_id:
			queryset = queryset.filter(variants__color_id=color_id).distinct()

		size_id = request.query_params.get("size")
		if size_id:
			queryset = queryset.filter(variants__size_id=size_id).distinct()

		product_type = request.query_params.get("type")
		if product_type:
			queryset = queryset.filter(product_type=product_type)

		condition = request.query_params.get("condition")
		if condition:
			queryset = queryset.filter(condition=condition)

		availability = request.query_params.get("availability")
		if availability and availability.lower() == "true":
			queryset = queryset.filter(is_active=True)

		# Limit results
		limit = min(int(request.query_params.get("limit", 10)), 100)

		# Get random products
		product_ids = list(queryset.values_list("id", flat=True))
		if not product_ids:
			return Response([])

		random_ids = random.sample(product_ids, min(limit, len(product_ids)))
		random_products = Product.objects.filter(id__in=random_ids).prefetch_related(
			"images", "variants"
		).select_related("seller", "category")

		serializer = self.get_serializer(random_products, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=["get"])
	def search_suggestions(self, request):
		"""Get search suggestions for product names (minimum 3 characters required)"""
		query = request.query_params.get("q", "").strip()

		# Validate minimum character requirement
		if len(query) < 3:
			return Response(
				{"error": "Search query must be at least 3 characters long"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		# Get published products matching the query
		suggestions = (
			self.get_queryset()
			.filter(name__icontains=query)
			.values_list("name", flat=True)
			.distinct()[:10]
		)

		return Response({"suggestions": list(suggestions)})

