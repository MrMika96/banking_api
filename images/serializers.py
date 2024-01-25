from rest_framework import serializers

from images.models import Image


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    url = serializers.CharField(read_only=True)

    class Meta:
        model = Image
        fields = ["id", "image", "url"]
