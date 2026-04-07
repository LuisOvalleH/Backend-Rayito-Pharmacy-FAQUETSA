from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        AGOTADO = "agotado", "Agotado"
        DESCONTINUADO = "descontinuado", "Descontinuado"

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen = models.URLField(blank=True)
    formula = models.TextField(blank=True, default="")
    registro = models.CharField(max_length=120, blank=True, default="")
    presentacion = models.CharField(max_length=120, blank=True, default="")

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        db_index=True,
    )

    # ── NUEVO: producto destacado ──────────────────────────────────────
    destacado = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Aparece en la sección de destacados del Home y primero en el catálogo.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Destacados primero, luego por fecha de actualización
        ordering = ["-destacado", "-updated_at"]

    def __str__(self):
        return self.nombre

    @property
    def disponible(self):
        return self.estado == self.Estado.DISPONIBLE


class ImagenInformacion(models.Model):
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, default="")
    imagen = models.URLField()
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Imagen de información"
        verbose_name_plural = "Imágenes de información"
        ordering = ["orden", "-updated_at"]

    def __str__(self):
        return self.titulo


class SiteConfig(models.Model):
    """
    Configuración global del sitio — singleton (siempre pk=1).
    El admin puede ajustar cuántos productos se muestran por página
    y cuántas imágenes informativas se muestran en el Home.
    """
    productos_por_pagina = models.PositiveSmallIntegerField(
        default=12,
        validators=[MinValueValidator(4), MaxValueValidator(48)],
        help_text="Cuántos productos se muestran por página en el catálogo público (4–48).",
    )
    max_imagenes_home = models.PositiveSmallIntegerField(
        default=6,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Máximo de imágenes informativas visibles en el Home (1–20).",
    )
    max_destacados_home = models.PositiveSmallIntegerField(
        default=8,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Máximo de productos destacados visibles en la sección de Home (1–20).",
    )

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuración del sitio"

    def __str__(self):
        return "Configuración del sitio"

    @classmethod
    def get(cls):
        """Devuelve la instancia única, creándola si no existe."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
