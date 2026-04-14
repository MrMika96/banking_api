"""Module with serializers for image app."""
from rest_framework import serializers

from images.models import Image


class ImageSerializer(serializers.ModelSerializer):
    """Image serializer."""

    image = serializers.ImageField(write_only=True)
    url = serializers.CharField(read_only=True)

    class Meta:
        """Meta."""

        model = Image
        fields = ["id", "image", "url"]
