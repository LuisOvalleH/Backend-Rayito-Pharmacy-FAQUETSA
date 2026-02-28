from rest_framework import serializers
from .models import Producto, Categoria
from .cloudinary_service import upload_product_image


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre"]


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
