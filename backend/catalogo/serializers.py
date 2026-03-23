from rest_framework import serializers
from .models import Producto, Categoria, ImagenInformacion
from .cloudinary_service import upload_product_image
from django.utils.text import slugify


class CategoriaSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)  # el front nunca lo manda

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
    # extra solo para lectura (para el frontend)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    imagen_file = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Producto
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        image_file = attrs.get("imagen_file")
        image_url = attrs.get("imagen")
        
        if self.instance is None and not image_file and not image_url:
            raise serializers.ValidationError(
                {"imagen_file": "La imagen es obligatoria al crear un producto."}
            )
        
        if image_file:
            content_type = getattr(image_file, "content_type", "")
            if not content_type.startswith("image/"):
                raise serializers.ValidationError(
                    {"imagen_file": "Solo se permiten archivos de imagen."}
                )
            
            max_size = 5 * 1024 * 1024  # 5 MB
            if image_file.size > max_size:
                raise serializers.ValidationError(
                    {"imagen_file": "La imagen no puede superar 5 MB."}
                )
        return attrs

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
      
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a Q0.00.")
        if value > 999_999:
            raise serializers.ValidationError("El precio no puede superar Q999,999.00.")
        return value

    def validate_imagen_file(self, value):
        if value is None:
            return value

        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
        max_size_mb = 5

        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Solo se permiten imágenes en formato JPEG, PNG, WebP o GIF."
                )
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
            f"La imagen no puede superar {max_size_mb}MB."
            )
        return value

class ImagenInformacionSerializer(serializers.ModelSerializer):
    imagen_file = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ImagenInformacion
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        imagen_file = attrs.get("imagen_file")
        imagen_url = attrs.get("imagen")

        if self.instance is None and not imagen_file and not imagen_url:
            raise serializers.ValidationError({
                "imagen_file": "La imagen es obligatoria al crear un registro de información."
            })

        if imagen_file:
            allowed_types = ["image/jpeg", "image/png", "image/webp"]
            if content_type not in allowed_types:
                raise serializers.ValidationError({
                    "imagen_file": "Solo se permiten JPG, PNG o WEBP."
                })
            
            content_type = getattr(imagen_file, "content_type", "")
            if not content_type.startswith("image/"):
                raise serializers.ValidationError({
                    "imagen_file": "Solo se permiten archivos de imagen."
                })

            max_size = 5 * 1024 * 1024  # 5 MB
            if imagen_file.size > max_size:
                raise serializers.ValidationError({
                    "imagen_file": "La imagen no puede superar 5 MB."
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
