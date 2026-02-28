from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Categoria, Producto


class CatalogSecurityTests(APITestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Analgesicos", slug="analgesicos")
        self.producto = Producto.objects.create(
            nombre="Paracetamol",
            descripcion="500mg",
            precio=10,
            categoria=self.categoria,
            estado=Producto.Estado.DISPONIBLE,
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass123",
            is_staff=True,
        )
        self.normal_user = User.objects.create_user(
            username="cliente",
            password="clientepass123",
            is_staff=False,
        )

    def _login(self, username, password):
        response = self.client.post(
            "/api/auth/login/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"]

    def test_public_can_list_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_create_product(self):
        access = self._login("cliente", "clientepass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(
            "/api/products/",
            {
                "nombre": "Ibuprofeno",
                "descripcion": "400mg",
                "precio": "15.00",
                "categoria": self.categoria.id,
                "estado": Producto.Estado.DISPONIBLE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_product(self):
        access = self._login("admin", "adminpass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(
            "/api/products/",
            {
                "nombre": "Amoxicilina",
                "descripcion": "500mg",
                "precio": "20.00",
                "categoria": self.categoria.id,
                "estado": Producto.Estado.DISPONIBLE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_me_returns_staff_flag(self):
        access = self._login("admin", "adminpass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "admin")
        self.assertTrue(response.data["is_staff"])
