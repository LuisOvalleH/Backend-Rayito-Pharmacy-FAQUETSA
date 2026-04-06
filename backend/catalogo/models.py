from django.db import models


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.nombre

    @property
    def disponible(self):
        # Para el front: True solo si está disponible
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