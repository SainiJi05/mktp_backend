from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from apps.common.models import Carousel, Section, SectionProduct, MarketplaceProduct
from apps.common.serializers import (
	CarouselSerializer,
	SectionSerializer,
	SectionProductSerializer,
	MarketplaceProductSerializer
)
from apps.accounts.permissions import IsAdmin


class CarouselViewSet(viewsets.ModelViewSet):
	"""
	Carousel API for home page display
	- GET: Anyone can fetch carousels
	- POST/PUT/DELETE: Only admin can create/edit/delete
	"""
	queryset = Carousel.objects.filter(is_active=True)
	serializer_class = CarouselSerializer

	def get_permissions(self):
		if self.action in ["list", "retrieve"]:
			return [permissions.AllowAny()]
		return [IsAdmin()]


class SectionViewSet(viewsets.ModelViewSet):
	"""
	Section API for multiple product sections (Featured, Most Sells, New Comers, etc)
	- GET: Anyone can fetch sections
	- POST/PUT/DELETE: Only admin can create/edit/delete sections
	"""
	queryset = Section.objects.filter(is_active=True)
	serializer_class = SectionSerializer

	def get_permissions(self):
		if self.action in ["list", "retrieve"]:
			return [permissions.AllowAny()]
		return [IsAdmin()]

	@action(detail=True, methods=["post"], permission_classes=[IsAdmin])
	def add_product(self, request, pk=None):
		"""Add a product to a section"""
		section = self.get_object()
		product_id = request.data.get("product_id")
		order = request.data.get("order", 0)

		if not product_id:
			return Response(
				{"error": "product_id is required"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			section_product = SectionProduct.objects.create(
				section=section,
				product_id=product_id,
				order=order
			)
			serializer = SectionProductSerializer(section_product)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		except Exception as e:
			return Response(
				{"error": str(e)},
				status=status.HTTP_400_BAD_REQUEST
			)

	@action(detail=True, methods=["delete"], permission_classes=[IsAdmin])
	def remove_product(self, request, pk=None):
		"""Remove a product from a section"""
		section = self.get_object()
		product_id = request.query_params.get("product_id")

		if not product_id:
			return Response(
				{"error": "product_id is required"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			section_product = SectionProduct.objects.get(
				section=section,
				product_id=product_id
			)
			section_product.delete()
			return Response(
				{"message": "Product removed from section"},
				status=status.HTTP_204_NO_CONTENT
			)
		except SectionProduct.DoesNotExist:
			return Response(
				{"error": "Product not found in section"},
				status=status.HTTP_404_NOT_FOUND
			)

	@action(detail=True, methods=["put"], permission_classes=[IsAdmin])
	def update_product_order(self, request, pk=None):
		"""Update product order in a section"""
		section = self.get_object()
		product_id = request.data.get("product_id")
		order = request.data.get("order")

		if not product_id or order is None:
			return Response(
				{"error": "product_id and order are required"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			section_product = SectionProduct.objects.get(
				section=section,
				product_id=product_id
			)
			section_product.order = order
			section_product.save()
			serializer = SectionProductSerializer(section_product)
			return Response(serializer.data, status=status.HTTP_200_OK)
		except SectionProduct.DoesNotExist:
			return Response(
				{"error": "Product not found in section"},
				status=status.HTTP_404_NOT_FOUND
			)


class MarketplaceProductViewSet(viewsets.ModelViewSet):
	"""
	Marketplace API for special product placements
	- GET: Anyone can fetch marketplace products
	- POST/PUT/DELETE: Only admin can create/edit/delete
	"""
	queryset = MarketplaceProduct.objects.filter(is_active=True)
	serializer_class = MarketplaceProductSerializer

	def get_permissions(self):
		if self.action in ["list", "retrieve"]:
			return [permissions.AllowAny()]
		return [IsAdmin()]

	@action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
	def by_placement(self, request):
		"""Get marketplace products filtered by placement name"""
		placement_name = request.query_params.get("placement_name")

		if not placement_name:
			return Response(
				{"error": "placement_name is required"},
				status=status.HTTP_400_BAD_REQUEST
			)

		products = self.get_queryset().filter(placement_name=placement_name)
		serializer = self.get_serializer(products, many=True)
		return Response(serializer.data)
