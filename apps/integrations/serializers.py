from django.db import models
from rest_framework import serializers


class MakePaymentSerializer(serializers.Serializer):
	order_id = serializers.IntegerField(min_value=1)


class VerifyPaymentSerializer(serializers.Serializer):
	order_id = serializers.IntegerField(min_value=1)
	razorpay_order_id = serializers.CharField(max_length=120)
	razorpay_payment_id = serializers.CharField(max_length=120)
	razorpay_signature = serializers.CharField(max_length=255)


class VTONTryOnSerializer(serializers.Serializer):
	class CategoryChoices(models.TextChoices):
		TOPS = "tops", "tops"
		BOTTOMS = "bottoms", "bottoms"
		ONE_PIECES = "one-pieces", "one-pieces"

	person_image = serializers.ImageField()
	garment_image = serializers.ImageField()
	category = serializers.ChoiceField(choices=CategoryChoices.choices)
	timeout = serializers.IntegerField(min_value=30, max_value=600, required=False, default=300)
