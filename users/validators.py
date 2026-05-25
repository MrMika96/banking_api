from django.core.exceptions import ValidationError
from PIL import Image as PILImage


def validate_profile_image(value):
    """Validate image type and size."""
    # Проверка размера (максимум 500KB)
    if value.size > 500 * 1024:
        raise ValidationError(
            f"Image size too large. Max 500KB, got {value.size // 1024}KB"
        )

    # Проверка типа через PIL
    try:
        img = PILImage.open(value)
        if img.format not in ["JPEG", "PNG"]:
            raise ValidationError("Only JPEG and PNG images are allowed")
        value.seek(0)
    except Exception:
        raise ValidationError("Invalid image file")
