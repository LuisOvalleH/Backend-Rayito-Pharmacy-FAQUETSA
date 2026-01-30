from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'', ProductoViewSet, basename='producto_em[ty]')

urlpatterns = router.urls