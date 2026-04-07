from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet, ImagenInformacionViewSet, ProductImageUploadView, ContactoView, ServicioViewSet, PasoProcesoViewSet, ConfianzaViewSet

router = DefaultRouter()
router.register(r"products", ProductoViewSet, basename="products")
router.register(r"categorias", CategoriaViewSet, basename="categorias")
router.register(r"imagenes-informacion", ImagenInformacionViewSet, basename="imagenes-informacion")
router.register(r"servicios",  ServicioViewSet, basename="servicios")
router.register(r"pasos",  PasoProcesoViewSet, basename="pasos")
router.register(r"confianza",  ConfianzaViewSet, basename="confianza")


urlpatterns = [
    path("", include(router.urls)),
    path("uploads/product-image/", ProductImageUploadView.as_view(), name="product_image_upload"),
    path("contacto/", ContactoView.as_view(), name="contacto")
    
    
]


