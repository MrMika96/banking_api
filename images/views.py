"""Module with views for image app."""
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny

from images.models import Image
from images.serializers import ImageSerializer
from . import docs


@extend_schema_view(**docs.get_images_docs())
class ImageViewSet(viewsets.ModelViewSet):
    """Image view set."""

    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser,)
    queryset = Image.objects.all()
    permission_classes = [AllowAny]
