from rest_framework import serializers

from .models import Accrual, Sale


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


class SaleSerializer(serializers.ModelSerializer):
    """Sale serializer."""

    class Meta:
        """Meta class."""

        model = Sale
        fields = "__all__"

    def validate(self, data):
        """Check the existence of such a record."""
        data = super().validate(data)
        obj = Sale.objects.filter(**data).first()
        if obj:
            raise serializers.ValidationError(
                f"Запись {str(obj)} уже существует!"
            )
        return data
