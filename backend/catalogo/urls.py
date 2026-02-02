from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet

router = DefaultRouter()
router.register(r"products", ProductoViewSet, basename="products")
router.register(r"categorias", CategoriaViewSet, basename="categorias")

urlpatterns = [
    path("", include(router.urls)),
]
