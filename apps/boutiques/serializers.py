from rest_framework import serializers

from apps.boutiques.models import Boutique


class BoutiqueSerializer(serializers.ModelSerializer):
	owner_id = serializers.IntegerField(source="owner.id", read_only=True)

	class Meta:
		model = Boutique
		fields = [
			"id",
			"owner_id",
			"name",
			"description",
			"phone",
			"email",
			"address",
			"city",
			"state",
			"country",
			"status",
			"is_active",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "status", "created_at", "updated_at", "owner_id"]
