from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import Address, User


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = [
			"id",
			"email",
			"phone",
			"first_name",
			"last_name",
			"role",
			"is_verified",
			"date_joined",
		]
		read_only_fields = ["id", "is_verified", "date_joined"]


class AddressSerializer(serializers.ModelSerializer):
	class Meta:
		model = Address
		fields = [
			"id",
			"name",
			"phone",
			"line1",
			"line2",
			"city",
			"state",
			"postal_code",
			"country",
			"is_default",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "created_at", "updated_at"]


class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=8)

	class Meta:
		model = User
		fields = ["email", "password", "phone", "first_name", "last_name", "role"]

	def validate_role(self, value: str) -> str:
		allowed_roles = {
			User.Role.CUSTOMER,
			User.Role.BOUTIQUE_OWNER,
			User.Role.MANUFACTURER,
		}
		if value not in allowed_roles:
			raise serializers.ValidationError("Invalid role for public registration.")
		return value

	def create(self, validated_data):
		password = validated_data.pop("password")
		return User.objects.create_user(password=password, **validated_data)


class AccessTokenSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user: User):
		token = super().get_token(user)
		token["role"] = user.role
		token["email"] = user.email
		return token

	def validate(self, attrs):
		data = super().validate(attrs)
		data.pop("refresh", None)
		return data
