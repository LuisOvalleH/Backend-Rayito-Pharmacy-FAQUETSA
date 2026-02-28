from django.conf import settings
from rest_framework.exceptions import ValidationError

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:  # pragma: no cover - handled at runtime
    cloudinary = None


def upload_product_image(file_obj):
    if not file_obj:
        return None

    if cloudinary is None:
        raise ValidationError(
            {"imagen_file": "Cloudinary no esta instalado en el backend."}
        )

    if not all(
        [
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        ]
    ):
        raise ValidationError(
            {"imagen_file": "Faltan credenciales de Cloudinary en el archivo .env."}
        )

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

    result = cloudinary.uploader.upload(
        file_obj,
        folder=settings.CLOUDINARY_UPLOAD_FOLDER,
        resource_type="image",
    )
    return result.get("secure_url") or result.get("url")
