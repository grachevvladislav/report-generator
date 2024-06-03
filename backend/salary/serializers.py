from rest_framework import serializers

from .models import Accrual


class AccrualSerializer(serializers.ModelSerializer):
    """Accrual serializer."""

    class Meta:
        """Meta class."""

        model = Accrual
        fields = "__all__"

    def validate(self, data):
        """Check the existence of such a record."""
        obj = Accrual.objects.filter(**data).first()
        if obj:
            raise serializers.ValidationError(
                f"Запись {str(obj)} уже существует!"
            )
        return data
