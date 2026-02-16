from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import Address, User
from apps.accounts.serializers import (
	AccessTokenSerializer,
	AddressSerializer,
	RegisterSerializer,
	UserSerializer,
)


class RegisterView(generics.CreateAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
	permission_classes = [permissions.AllowAny]
	serializer_class = AccessTokenSerializer


class MeView(generics.RetrieveUpdateAPIView):
	serializer_class = UserSerializer

	def get_object(self):
		return self.request.user


class AddressViewSet(viewsets.ModelViewSet):
	serializer_class = AddressSerializer

	def get_queryset(self):
		if getattr(self, "swagger_fake_view", False):
			return Address.objects.none()
		if not self.request.user.is_authenticated:
			return Address.objects.none()
		return Address.objects.filter(user=self.request.user).order_by("-created_at")

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)
