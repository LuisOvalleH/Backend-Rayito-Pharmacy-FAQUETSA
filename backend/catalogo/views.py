from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer
from .cloudinary_service import upload_product_image


class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        # GET público (list/retrieve), escritura solo admin
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]


class ProductoViewSet(ModelViewSet):
    queryset = Producto.objects.select_related("categoria").all().order_by("-updated_at")
    serializer_class = ProductoSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        # GET público (list/retrieve), escritura solo admin
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )


class ProductImageUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            raise ValidationError({"file": "Debes seleccionar una imagen."})

        image_url = upload_product_image(file_obj)
        return Response({"url": image_url}, status=status.HTTP_201_CREATED)
