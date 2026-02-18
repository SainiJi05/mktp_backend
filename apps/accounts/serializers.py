from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import Address, BankDetails, User


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


class BankDetailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = BankDetails
		fields = [
			"id",
			"account_holder_name",
			"account_number",
			"ifsc_code",
			"upi_id",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "created_at", "updated_at"]

	def validate(self, attrs):
		bank_fields = [
			"account_holder_name",
			"account_number",
			"ifsc_code",
		]
		instance = self.instance
		def field_value(field_name):
			if field_name in attrs:
				return attrs.get(field_name)
			return getattr(instance, field_name, None) if instance else None
		has_any_bank_field = any(field_value(field) for field in bank_fields)
		if has_any_bank_field:
			missing = [field for field in bank_fields if not field_value(field)]
			if missing:
				raise serializers.ValidationError(
					{"bank_details": f"Missing required bank fields: {', '.join(missing)}"}
				)
		if instance:
			upi_value = attrs.get("upi_id", instance.upi_id)
		else:
			upi_value = attrs.get("upi_id")
		if not has_any_bank_field and not upi_value:
			raise serializers.ValidationError(
				{"upi_id": "Provide either a UPI ID or complete bank details."}
			)
		return super().validate(attrs)


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
