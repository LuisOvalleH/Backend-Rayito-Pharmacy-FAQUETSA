from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet, ImagenInformacionViewSet, AdminViewSet, ProductImageUploadView

router = DefaultRouter()
router.register(r"products", ProductoViewSet, basename="products")
router.register(r"categorias", CategoriaViewSet, basename="categorias")
router.register(r"admins", AdminViewSet, basename="admins")
router.register(r"imagenes-informacion", ImagenInformacionViewSet, basename="imagenes-informacion")

urlpatterns = [
    path("", include(router.urls)),
    path("uploads/product-image/", ProductImageUploadView.as_view(), name="product_image_upload"),
]
