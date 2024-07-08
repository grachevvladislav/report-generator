from rest_framework import serializers

from .models import SalaryCertificate


class SalaryCertificateSerializer(serializers.ModelSerializer):
    """SalaryCertificate serializer."""

    class Meta:
        """Meta class."""

        model = SalaryCertificate
        fields = "__all__"
