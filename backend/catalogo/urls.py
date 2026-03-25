from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet, AdminViewSet

router = DefaultRouter()
router.register(r"products", ProductoViewSet, basename="products")
router.register(r"categorias", CategoriaViewSet, basename="categorias")
router.register(r"admins", AdminViewSet, basename="admins")

urlpatterns = [
    path("", include(router.urls)),
]