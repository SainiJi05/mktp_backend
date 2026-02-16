from rest_framework import permissions, viewsets
from apps.wishlist.models import WishlistItem
from apps.wishlist.serializers import WishlistItemSerializer


class WishlistItemViewSet(viewsets.ModelViewSet):
	serializer_class = WishlistItemSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return WishlistItem.objects.none()
		if not self.request.user.is_authenticated:
			return WishlistItem.objects.none()
		return WishlistItem.objects.filter(user=self.request.user).select_related("product", "variant")

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)
