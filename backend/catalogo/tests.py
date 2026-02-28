from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("imagen_file", response.data)

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

    @patch("catalogo.serializers.upload_product_image")
    def test_admin_can_create_product_with_image_upload(self, mock_upload_product_image):
        mock_upload_product_image.return_value = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
        access = self._login("admin", "adminpass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        image = SimpleUploadedFile(
            "producto.gif",
            (
                b"GIF87a\x01\x00\x01\x00\x80\x00\x00"
                b"\x00\x00\x00\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,"
                b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )

        response = self.client.post(
            "/api/products/",
            {
                "nombre": "Vitamina C",
                "descripcion": "Tabletas",
                "precio": "12.50",
                "categoria": str(self.categoria.id),
                "estado": Producto.Estado.DISPONIBLE,
                "imagen_file": image,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["imagen"],
            "https://res.cloudinary.com/demo/image/upload/sample.jpg",
        )
        mock_upload_product_image.assert_called_once()
