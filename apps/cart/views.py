from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.cart.models import Cart, CartItem
from apps.cart.serializers import CartItemAddSerializer, CartItemSerializer, CartSerializer


class CartView(generics.RetrieveAPIView):
	serializer_class = CartSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		cart, _ = Cart.objects.get_or_create(user=self.request.user)
		return cart


class CartItemViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return CartItem.objects.none()
		if not self.request.user.is_authenticated:
			return CartItem.objects.none()
		cart, _ = Cart.objects.get_or_create(user=self.request.user)
		return CartItem.objects.filter(cart=cart).select_related("product", "variant")

	def get_serializer_class(self):
		if self.action == "create":
			return CartItemAddSerializer
		return CartItemSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		product = serializer.validated_data["product"]
		variant = serializer.validated_data.get("variant")
		if variant and variant.product_id != product.id:
			raise ValidationError("Variant does not belong to the selected product.")
		cart, _ = Cart.objects.get_or_create(user=request.user)
		item, created = CartItem.objects.get_or_create(
			cart=cart,
			product=product,
			variant=variant,
			defaults={
				"quantity": serializer.validated_data["quantity"],
				"price_snapshot": variant.price_override if variant and variant.price_override else product.base_price,
			},
		)
		if not created:
			item.quantity += serializer.validated_data["quantity"]
			item.save(update_fields=["quantity", "updated_at"])
		return Response(CartItemSerializer(item).data, status=201)
