"""Module with documentation for images."""
from drf_spectacular.utils import extend_schema

IMAGE_TAG = "Images"


def get_images_docs() -> dict:
    """Return documentation for images."""
    return {
        "create": extend_schema(
            tags=[IMAGE_TAG],
            description="Uploading images to the system",
            summary="Image upload"
        ),
        "retrieve":  extend_schema(
            tags=[IMAGE_TAG],
            description="Getting image by id",
            summary="Get image"
        ),
        "destroy":  extend_schema(
            tags=[IMAGE_TAG],
            description="Removing an image from the system by its id",
            summary="Deleting an image",
        )
    }
