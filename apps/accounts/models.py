from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
	def create_user(self, email: str, password: str | None = None, **extra_fields):
		if not email:
			raise ValueError("Email is required")
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email: str, password: str | None = None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("role", User.Role.ADMIN)
		if extra_fields.get("is_staff") is not True:
			raise ValueError("Superuser must have is_staff=True")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Superuser must have is_superuser=True")
		return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	class Role(models.TextChoices):
		ADMIN = "admin", "Admin"
		BOUTIQUE_OWNER = "boutique_owner", "Boutique Owner"
		CUSTOMER = "customer", "Customer"
		MANUFACTURER = "manufacturer", "Manufacturer"

	email = models.EmailField(unique=True)
	phone = models.CharField(max_length=20, blank=True)
	first_name = models.CharField(max_length=120, blank=True)
	last_name = models.CharField(max_length=120, blank=True)
	role = models.CharField(max_length=32, choices=Role.choices, default=Role.CUSTOMER)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_verified = models.BooleanField(default=False)
	date_joined = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS: list[str] = []

	objects = UserManager()

	def __str__(self) -> str:
		return self.email


class Address(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
	name = models.CharField(max_length=150)
	phone = models.CharField(max_length=20)
	line1 = models.CharField(max_length=255)
	line2 = models.CharField(max_length=255, blank=True)
	city = models.CharField(max_length=120)
	state = models.CharField(max_length=120)
	postal_code = models.CharField(max_length=20)
	country = models.CharField(max_length=120, default="India")
	is_default = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.city})"
