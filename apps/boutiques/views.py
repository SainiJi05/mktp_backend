from rest_framework import permissions, viewsets

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsAdminOrBoutiqueOwner, IsBoutiqueOwner
from apps.admin_api.models import MarketplaceSettings
from apps.boutiques.models import Boutique
from apps.boutiques.serializers import BoutiqueSerializer


class BoutiqueViewSet(viewsets.ModelViewSet):
	serializer_class = BoutiqueSerializer

	def get_queryset(self):
		user = self.request.user
		if user.is_authenticated and user.role == User.Role.ADMIN:
			return Boutique.objects.all()
		if user.is_authenticated and user.role == User.Role.BOUTIQUE_OWNER:
			return Boutique.objects.filter(owner=user)
		return Boutique.objects.filter(status=Boutique.Status.APPROVED, is_active=True)

	def get_permissions(self):
		if self.action in {"list", "retrieve"}:
			return [permissions.AllowAny()]
		if self.action in {"create", "update", "partial_update", "destroy"}:
			return [IsAdminOrBoutiqueOwner()]
		return [permissions.IsAuthenticated()]

	def perform_create(self, serializer):
		settings = MarketplaceSettings.get_settings()
		status = Boutique.Status.APPROVED if settings.auto_approve_boutiques else Boutique.Status.PENDING
		serializer.save(owner=self.request.user, status=status)
