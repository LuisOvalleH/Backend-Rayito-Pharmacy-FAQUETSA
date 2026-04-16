from urllib import request, response

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from .serializers import AdminSerializer
from .permissions import IsSuperAdmin

from .utils import registrar_historial
from rest_framework.decorators import api_view, permission_classes, action

from django.utils import timezone

from .models import Producto, Categoria, ImagenInformacion, Servicio, PasoProceso, Confianza, Historial, ConfiguracionSistema
from .serializers import ProductoSerializer, CategoriaSerializer, ImagenInformacionSerializer, ServicioSerializer, PasoProcesoSerializer, ConfianzaSerializer
from .cloudinary_service import upload_product_image


class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        # GET público (list/retrieve), escritura solo admin
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        registrar_historial(
            request.user,
            "crear",
            "categorias",
            f"Creó la categoría {response.data['nombre']}"
        )

        return response
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        response = super().update(request, *args, **kwargs)

        registrar_historial(
            request.user,
            "editar",
            "categorias",
            f"Editó la categoría {instance.nombre} a {response.data['nombre']}"
        )

        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        registrar_historial(
            request.user,
            "eliminar",
            "categorias",
            f"Eliminó la categoría {instance.nombre}"
        )

        return super().destroy(request, *args, **kwargs)


class ProductoViewSet(ModelViewSet):
    queryset = Producto.objects.select_related("categoria").all().order_by("-updated_at")
    serializer_class = ProductoSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        # GET público (list/retrieve), escritura solo admin
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        registrar_historial(
            request.user,
            "crear",
            "productos",
            f"Creó un producto llamado {response.data['nombre']}"
        )

        return response
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        response = super().update(request, *args, **kwargs)

        registrar_historial(
            request.user,
            "editar",
            "productos",
            f"Editó el producto {instance.nombre}"
        )

        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        registrar_historial(
            request.user,
            "eliminar",
            "productos",
            f"Eliminó el producto {instance.nombre}"
        )

        return super().destroy(request, *args, **kwargs)
    


class ImagenInformacionViewSet(ModelViewSet):
    queryset = ImagenInformacion.objects.all().order_by("orden", "-updated_at")
    serializer_class = ImagenInformacionSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # para manejar roles
        if user.is_superuser:
            role = "superadmin"
        elif user.is_staff:
            role = "admin"
        else:
            role = "user"

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "role": role,  
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

class AdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        registrar_historial(
            request.user,
            "crear",
            "usuarios",
            f"Creó un nuevo usuario llamado {response.data['username']} con el rol de {'superadmin' if response.data['is_superuser'] else 'admin'}"
        )

        return response
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        response = super().update(request, *args, **kwargs)

        registrar_historial(
            request.user,
            "editar",
            "usuarios",
            f"Editó el usuario {instance.username}"
        )

        return response
    
    @action(detail=True, methods=["patch"])
    def toggle_active(self, request, pk=None):
        user = self.get_object()

        user.is_active = not user.is_active
        user.save()

        estado = "activó" if user.is_active else "desactivó"

        registrar_historial(
            request.user,
            "editar",
            "usuarios",
            f"{estado} al usuario {user.username}"
        )

        return Response({
            "status": f"Usuario {estado}",
            "is_active": user.is_active
        })


@api_view(["GET"])
@permission_classes([IsSuperAdmin])
def historial_list(request):
    modulo = request.GET.get("modulo")

    historial = Historial.objects.all().order_by("-fecha")

    if modulo:
        historial = historial.filter(modulo=modulo)

    data = [
        {
            "usuario": h.usuario.username if h.usuario else "N/A",
            "accion": h.accion,
            "fecha": timezone.localtime(h.fecha).strftime("%Y-%m-%d"),
            "hora": timezone.localtime(h.fecha).strftime("%H:%M:%S"),
            "detalle": h.descripcion,
          
        }
        for h in historial
    ]

    return Response(data)




@api_view(['GET', 'POST'])
@permission_classes([IsSuperAdmin])
def configuracion_limpieza(request):
    config, _ = ConfiguracionSistema.objects.get_or_create(id=1)

    if request.method == 'GET':
        return Response({'meses': config.meses_retencion_historial})

    if request.method == 'POST':
        meses = request.data.get('meses')
        config.meses_retencion_historial = meses
        config.save()
        return Response({'status': 'Configuración actualizada'})

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
