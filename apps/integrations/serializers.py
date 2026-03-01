from django.db import models
from rest_framework import serializers


class MakePaymentSerializer(serializers.Serializer):
	order_id = serializers.IntegerField(min_value=1)


class MakePaymentResponseSerializer(serializers.Serializer):
	order_id = serializers.IntegerField()
	razorpay_order_id = serializers.CharField()
	razorpay_key_id = serializers.CharField()
	amount = serializers.IntegerField()
	currency = serializers.CharField()


class VerifyPaymentSerializer(serializers.Serializer):
	order_id = serializers.IntegerField(min_value=1)
	razorpay_order_id = serializers.CharField(max_length=120)
	razorpay_payment_id = serializers.CharField(max_length=120)
	razorpay_signature = serializers.CharField(max_length=255)


class VerifyPaymentResponseSerializer(serializers.Serializer):
	order_id = serializers.IntegerField()
	payment_status = serializers.CharField()
	razorpay_order_id = serializers.CharField()
	razorpay_payment_id = serializers.CharField()


class VTONTryOnSerializer(serializers.Serializer):
	class CategoryChoices(models.TextChoices):
		TOPS = "tops", "tops"
		BOTTOMS = "bottoms", "bottoms"
		ONE_PIECES = "one-pieces", "one-pieces"

	person_image = serializers.ImageField()
	garment_image = serializers.ImageField()
	category = serializers.ChoiceField(choices=CategoryChoices.choices)
	timeout = serializers.IntegerField(min_value=30, max_value=600, required=False, default=300)


class VTONTryOnResponseSerializer(serializers.Serializer):
	output_image = serializers.CharField(help_text="Base64 encoded PNG image")
