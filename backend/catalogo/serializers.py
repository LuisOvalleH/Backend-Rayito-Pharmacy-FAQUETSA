from rest_framework import serializers
from .models import Producto, Categoria, ImagenInformacion, SiteConfig
from .cloudinary_service import upload_product_image, ALLOWED_CONTENT_TYPES, MIN_DIMENSION
from django.utils.text import slugify


class CategoriaSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug"]

    def validate_nombre(self, value):
        slug = slugify(value)
        qs = Categoria.objects.filter(slug=slug)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una categoría con ese nombre.")
        return value

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["nombre"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "nombre" in validated_data:
            validated_data["slug"] = slugify(validated_data["nombre"])
        return super().update(instance, validated_data)


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    imagen_file = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Producto
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate_imagen_file(self, value):
        if value is None:
            return value

        # Formato
        content_type = getattr(value, "content_type", "").lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Solo se permiten imágenes en formato JPG, PNG o WebP."
            )

        # Dimensiones mínimas
        try:
            from PIL import Image as PilImage
            value.seek(0)
            img = PilImage.open(value)
            w, h = img.size
            value.seek(0)
            if w < MIN_DIMENSION or h < MIN_DIMENSION:
                raise serializers.ValidationError(
                    f"La imagen debe tener al menos {MIN_DIMENSION}×{MIN_DIMENSION} px "
                    f"(recibida: {w}×{h} px)."
                )
        except serializers.ValidationError:
            raise
        except Exception:
            pass

        return value

    def validate(self, attrs):
        image_file = attrs.get("imagen_file")
        image_url = attrs.get("imagen")

        if self.instance is None and not image_file and not image_url:
            raise serializers.ValidationError(
                {"imagen_file": "La imagen es obligatoria al crear un producto."}
            )
        return attrs

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a Q0.00.")
        if value > 999_999:
            raise serializers.ValidationError("El precio no puede superar Q999,999.00.")
        return value

    def create(self, validated_data):
        image_file = validated_data.pop("imagen_file", None)
        if image_file:
            validated_data["imagen"] = upload_product_image(image_file)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image_file = validated_data.pop("imagen_file", None)
        if image_file:
            validated_data["imagen"] = upload_product_image(image_file)
        return super().update(instance, validated_data)


class ImagenInformacionSerializer(serializers.ModelSerializer):
    imagen_file = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ImagenInformacion
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate_imagen_file(self, value):
        if value is None:
            return value

        # Orden correcto: obtener content_type antes de usarlo
        content_type = getattr(value, "content_type", "").lower()

        if content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Solo se permiten imágenes JPG, PNG o WebP."
            )

        # Dimensiones mínimas
        try:
            from PIL import Image as PilImage
            value.seek(0)
            img = PilImage.open(value)
            w, h = img.size
            value.seek(0)
            if w < MIN_DIMENSION or h < MIN_DIMENSION:
                raise serializers.ValidationError(
                    f"La imagen debe tener al menos {MIN_DIMENSION}×{MIN_DIMENSION} px "
                    f"(recibida: {w}×{h} px)."
                )
        except serializers.ValidationError:
            raise
        except Exception:
            pass

        return value

    def validate(self, attrs):
        imagen_file = attrs.get("imagen_file")
        imagen_url = attrs.get("imagen")

        if self.instance is None and not imagen_file and not imagen_url:
            raise serializers.ValidationError({
                "imagen_file": "La imagen es obligatoria al crear un registro de información."
            })
        return attrs

    def create(self, validated_data):
        imagen_file = validated_data.pop("imagen_file", None)
        if imagen_file:
            validated_data["imagen"] = upload_product_image(imagen_file)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        imagen_file = validated_data.pop("imagen_file", None)
        if imagen_file:
            validated_data["imagen"] = upload_product_image(imagen_file)
        return super().update(instance, validated_data)


class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfig
        fields = [
            "productos_por_pagina",
            "max_imagenes_home",
            "max_destacados_home",
        ]
