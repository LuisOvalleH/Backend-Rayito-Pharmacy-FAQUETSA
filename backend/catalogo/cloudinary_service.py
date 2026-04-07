from django.conf import settings
from rest_framework.exceptions import ValidationError

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:  # pragma: no cover
    cloudinary = None

# Restricciones compartidas (usadas también en el serializer)
MIN_DIMENSION = 300                      # 300 px mínimo en cada lado
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


def _validate_image_file(file_obj):
    """
    Valida formato y dimensiones mínimas del archivo de imagen.
    No hay límite de tamaño: Cloudinary acepta archivos grandes y los optimiza.
    Lanza ValidationError si no cumple los requisitos.
    """
    if not file_obj:
        return

    # Formato permitido
    content_type = getattr(file_obj, "content_type", "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(
            {"imagen_file": "Solo se permiten imágenes JPG, PNG o WebP."}
        )

    # Dimensiones mínimas (requiere Pillow)
    try:
        from PIL import Image as PilImage
        file_obj.seek(0)
        img = PilImage.open(file_obj)
        width, height = img.size
        file_obj.seek(0)  # rebobinar para que Cloudinary lo lea después

        if width < MIN_DIMENSION or height < MIN_DIMENSION:
            raise ValidationError(
                {
                    "imagen_file": (
                        f"La imagen debe tener al menos {MIN_DIMENSION}×{MIN_DIMENSION} px "
                        f"(recibida: {width}×{height} px)."
                    )
                }
            )
    except ValidationError:
        raise
    except Exception:
        # Si Pillow no puede abrir el archivo, Cloudinary lo rechazará
        pass


def upload_product_image(file_obj):
    """
    Sube una imagen a Cloudinary con las transformaciones configuradas.
    Retorna la URL segura de la imagen subida.
    """
    if not file_obj:
        return None

    if cloudinary is None:
        raise ValidationError(
            {"imagen_file": "Cloudinary no está instalado en el backend."}
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

    # Validar antes de subir
    _validate_image_file(file_obj)

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
        # Transformaciones automáticas al subir:
        # - Redimensiona a máximo 800×800 sin distorsionar (crop=limit)
        # - Calidad automática optimizada
        # - Formato automático (avif/webp según el navegador)
        transformation=[
            {
                "width": 800,
                "height": 800,
                "crop": "limit",
                "quality": "auto:good",
                "fetch_format": "auto",
            }
        ],
        eager=[
            # Miniatura 300×300 con recorte centrado (para cards del catálogo)
            {
                "width": 300,
                "height": 300,
                "crop": "fill",
                "gravity": "auto",
                "quality": "auto:eco",
                "fetch_format": "auto",
            }
        ],
        eager_async=True,
    )

    return result.get("secure_url") or result.get("url")
