from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from .models import (
    Producto, 
    Categoria, 
    ImagenInformacion, 
    Servicio, 
    PasoProceso, 
    Confianza,
    SiteConfig
    )
from .serializers import (
    ProductoSerializer, 
    CategoriaSerializer, 
    ImagenInformacionSerializer, 
    ServicioSerializer, 
    PasoProcesoSerializer, 
    ConfianzaSerializer,
    SiteConfigSerializer
    )
from .cloudinary_service import upload_product_image


# ── Paginación dinámica ────────────────────────────────────────────────────────

class ProductoPagination(PageNumberPagination):
    """
    Paginación para el catálogo público.
    El page_size se lee de SiteConfig, configurable desde el panel admin.
    """
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_page_size(self, request):
        explicit = request.query_params.get(self.page_size_query_param)
        if explicit:
            try:
                size = int(explicit)
                return min(max(size, 1), self.max_page_size)
            except (ValueError, TypeError):
                pass
        return SiteConfig.get().productos_por_pagina


# ── ViewSets ──────────────────────────────────────────────────────────────────

class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]


class ProductoViewSet(ModelViewSet):
    serializer_class = ProductoSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Producto.objects.select_related("categoria").order_by("-updated_at")

        destacado = self.request.query_params.get("destacado")
        if destacado is not None:
            qs = qs.filter(destacado=destacado.lower() in {"1", "true", "yes"})

        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado__iexact=estado)

        categoria = self.request.query_params.get("categoria")
        if categoria:
            qs = qs.filter(categoria_id=categoria)

        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    @property
    def pagination_class(self):
        # Sin paginación para: panel admin (?admin=true) y destacados del Home
        es_admin = self.request.query_params.get("admin") == "true"
        es_destacados = self.request.query_params.get("destacado") is not None
        if es_admin or es_destacados:
            return None
        return ProductoPagination


class ImagenInformacionViewSet(ModelViewSet):
    serializer_class = ImagenInformacionSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = ImagenInformacion.objects.order_by("orden", "-updated_at")
        solo_activas = self.request.query_params.get("activas")
        if solo_activas is not None:
            qs = qs.filter(activa=True)
            limite = SiteConfig.get().max_imagenes_home
            qs = qs[:limite]
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]


# ── Vistas sueltas ─────────────────────────────────────────────────────────────

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        })


class ProductImageUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            raise ValidationError({"file": "Debes seleccionar una imagen."})
        image_url = upload_product_image(file_obj)
        return Response({"url": image_url}, status=status.HTTP_201_CREATED)


class ContactoView(APIView):
    def post(self, request):
        nombre = request.data.get("nombre")
        apellido = request.data.get("apellido")
        email = request.data.get("email")
        mensaje = request.data.get("mensaje")

        send_mail(
            subject="Nuevo mensaje desde formulario de contacto",
            message=f"""
Nombre: {nombre}
Apellido: {apellido}
Correo: {email}

Mensaje:
{mensaje}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            fail_silently=False,
        )

        return Response(
            {"message": "Correo enviado correctamente"},
            status=status.HTTP_200_OK
        )
    

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class PasoProcesoViewSet(viewsets.ModelViewSet):
    queryset = PasoProceso.objects.all()
    serializer_class = PasoProcesoSerializer

class ConfianzaViewSet(viewsets.ModelViewSet):
    queryset = Confianza.objects.all()
    serializer_class = ConfianzaSerializer
class SiteConfigView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        return Response(SiteConfigSerializer(SiteConfig.get()).data)

    def patch(self, request):
        config = SiteConfig.get()
        serializer = SiteConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
