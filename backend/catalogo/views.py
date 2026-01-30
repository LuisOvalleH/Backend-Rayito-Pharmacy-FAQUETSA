from rest_framework.viewsets import ModelViewSet
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer