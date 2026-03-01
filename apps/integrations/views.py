import base64
from io import BytesIO

import razorpay
import runpod
from django.conf import settings
from django.db import transaction
from django.http import FileResponse
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.integrations.serializers import (
	MakePaymentSerializer,
	VerifyPaymentSerializer,
	VTONTryOnSerializer,
)
from apps.orders.models import Order


def _get_razorpay_client():
	if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
		raise ValidationError("Razorpay keys are not configured.")
	return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _file_to_base64(file_obj) -> str:
	file_obj.seek(0)
	return base64.b64encode(file_obj.read()).decode("utf-8")


class MakePaymentView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, *args, **kwargs):
		serializer = MakePaymentSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		order = Order.objects.filter(id=serializer.validated_data["order_id"]).first()
		if order is None:
			raise ValidationError({"order_id": "Order not found."})

		if order.customer_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only create payment for your own order.")
		if order.payment_status == Order.PaymentStatus.PAID:
			raise ValidationError("Order is already paid.")

		client = _get_razorpay_client()
		amount_paise = int(order.total * 100)
		if amount_paise <= 0:
			raise ValidationError("Order total must be greater than 0.")

		rzp_order = client.order.create(
			{
				"amount": amount_paise,
				"currency": order.currency,
				"receipt": f"order_{order.id}",
				"notes": {
					"platform_order_id": str(order.id),
					"customer_id": str(order.customer_id),
				},
			}
		)

		order.razorpay_order_id = rzp_order.get("id", "")
		order.save(update_fields=["razorpay_order_id", "updated_at"])

		return Response(
			{
				"order_id": order.id,
				"razorpay_order_id": order.razorpay_order_id,
				"razorpay_key_id": settings.RAZORPAY_KEY_ID,
				"amount": rzp_order.get("amount"),
				"currency": rzp_order.get("currency"),
			},
			status=201,
		)


class VerifyPaymentView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		serializer = VerifyPaymentSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		payload = serializer.validated_data

		order = Order.objects.select_for_update().filter(id=payload["order_id"]).first()
		if order is None:
			raise ValidationError({"order_id": "Order not found."})

		if order.customer_id != request.user.id and request.user.role != User.Role.ADMIN:
			raise PermissionDenied("You can only verify payment for your own order.")
		if order.payment_status == Order.PaymentStatus.PAID:
			return Response(
				{
					"order_id": order.id,
					"payment_status": order.payment_status,
					"razorpay_order_id": order.razorpay_order_id,
					"razorpay_payment_id": order.razorpay_payment_id,
				}
			)

		razorpay_order_id = payload["razorpay_order_id"]
		if order.razorpay_order_id and razorpay_order_id != order.razorpay_order_id:
			raise ValidationError("Razorpay order id mismatch.")

		client = _get_razorpay_client()
		client.utility.verify_payment_signature(
			{
				"razorpay_order_id": razorpay_order_id,
				"razorpay_payment_id": payload["razorpay_payment_id"],
				"razorpay_signature": payload["razorpay_signature"],
			}
		)

		order.razorpay_order_id = razorpay_order_id
		order.razorpay_payment_id = payload["razorpay_payment_id"]
		order.razorpay_signature = payload["razorpay_signature"]
		order.payment_status = Order.PaymentStatus.PAID
		order.save(
			update_fields=[
				"razorpay_order_id",
				"razorpay_payment_id",
				"razorpay_signature",
				"payment_status",
				"updated_at",
			]
		)

		return Response(
			{
				"order_id": order.id,
				"payment_status": order.payment_status,
				"razorpay_order_id": order.razorpay_order_id,
				"razorpay_payment_id": order.razorpay_payment_id,
			}
		)


class VTONTryOnView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, *args, **kwargs):
		serializer = VTONTryOnSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		if not settings.RUNPOD_API_KEY or not settings.RUNPOD_VTON_ENDPOINT_ID:
			raise ValidationError("RunPod VTON settings are not configured.")

		runpod.api_key = settings.RUNPOD_API_KEY
		endpoint = runpod.Endpoint(settings.RUNPOD_VTON_ENDPOINT_ID)

		payload = {
			"input": {
				"person_image": _file_to_base64(serializer.validated_data["person_image"]),
				"garment_image": _file_to_base64(serializer.validated_data["garment_image"]),
				"category": serializer.validated_data["category"],
			}
		}

		response = endpoint.run_sync(payload, timeout=serializer.validated_data["timeout"])

		if not isinstance(response, dict):
			raise ValidationError("Unexpected RunPod response format.")

		error = response.get("error")
		if error:
			raise ValidationError({"runpod": error})

		output_image = response.get("output_image")
		if not output_image and isinstance(response.get("output"), dict):
			output_image = response["output"].get("output_image")

		if not output_image:
			raise ValidationError("RunPod response did not include output_image.")

		return Response({"output_image": output_image}, status=200)
