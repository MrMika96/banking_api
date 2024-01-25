from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny

from images.models import Image
from images.serializers import ImageSerializer


@extend_schema_view(
    create=extend_schema(
        description="Uploading images to the system", summary="Image upload"
    ),
    retrieve=extend_schema(description="Getting image by id", summary="Get image"),
    destroy=extend_schema(
        description="Removing an image from the system by its id",
        summary="Deleting an image",
    ),
)
class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser,)
    queryset = Image.objects.all()
    permission_classes = [AllowAny]
