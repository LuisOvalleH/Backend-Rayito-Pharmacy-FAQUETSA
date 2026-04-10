from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Categoria, ImagenInformacion, Historial
from .cloudinary_service import upload_product_image

class ImagenInformacionAdminForm(forms.ModelForm):
    imagen = forms.URLField(
        required=False,
        label="Imagen"
    )

    imagen_file = forms.ImageField(
        required=False,
        label="Subir imagen",
        help_text="Selecciona una imagen JPG, PNG o WEBP."
    )

    class Meta:
        model = ImagenInformacion
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        imagen = cleaned_data.get("imagen")
        archivo = cleaned_data.get("imagen_file")

        if not imagen and not archivo:
            raise forms.ValidationError("Debes proporcionar una URL o subir una imagen.")

        return cleaned_data

    def clean_imagen_file(self):
        archivo = self.cleaned_data.get("imagen_file")
        if not archivo:
            return archivo

        content_type = getattr(archivo, "content_type", "")
        if not content_type.startswith("image/"):
            raise forms.ValidationError("Solo se permiten archivos de imagen.")

        max_size = 5 * 1024 * 1024  # 5 MB
        if archivo.size > max_size:
            raise forms.ValidationError("La imagen no puede superar 5 MB.")

        return archivo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # columnas del listado
    list_display = (
        "id",
        "nombre",
        "categoria",
        "estado_badge",
        "precio",
        "imagen_link",
        "created_at",
        "updated_at",
    )

    # filtros a la derecha
    list_filter = ("estado", "categoria")

    # barra de búsqueda
    search_fields = ("nombre", "descripcion", "categoria__nombre")

    # orden default
    ordering = ("-updated_at",)

    # editar rápido desde listado
    list_editable = ("categoria", "precio")

    # campos por secciones cuando entras al form
    fieldsets = (
        ("Información principal", {
            "fields": ("nombre", "descripcion", "categoria")
        }),
        ("Precio y estado", {
            "fields": ("precio", "estado")
        }),
        ("Imagen", {
            "fields": ("imagen",)
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # para que no se editen manualmente
    readonly_fields = ("created_at", "updated_at")

    # acciones masivas
    actions = ("marcar_disponible", "marcar_agotado", "marcar_descontinuado")

    def estado_badge(self, obj):
        # Colores del badge según estado
        est = (obj.estado or "").upper()
        if "DES" in est:
            bg, fg = "#FEE2E2", "#991B1B"   # rojo suave
            label = "Descontinuado"
        elif "AGO" in est:
            bg, fg = "#FEF3C7", "#92400E"   # amarillo suave
            label = "Agotado"
        else:
            bg, fg = "#DCFCE7", "#166534"   # verde suave
            label = "Disponible"

        return format_html(
            '<span style="padding:6px 10px;border-radius:999px;'
            'background:{};color:{};font-weight:700;border:1px solid rgba(0,0,0,.08)">'
            '{}</span>',
            bg, fg, label
        )

    estado_badge.short_description = "Estado"
    estado_badge.admin_order_field = "estado"

    def imagen_link(self, obj):
        if not obj.imagen:
            return "-"
        return format_html('<a href="{}" target="_blank">Ver</a>', obj.imagen)

    imagen_link.short_description = "Imagen"

    # Acciones
    def marcar_disponible(self, request, queryset):
        queryset.update(estado=Producto.Estado.DISPONIBLE)
    marcar_disponible.short_description = "Marcar como DISPONIBLE"

    def marcar_agotado(self, request, queryset):
        queryset.update(estado=Producto.Estado.AGOTADO)
    marcar_agotado.short_description = "Marcar como AGOTADO"

    def marcar_descontinuado(self, request, queryset):
        queryset.update(estado=Producto.Estado.DESCONTINUADO)
    marcar_descontinuado.short_description = "Marcar como DESCONTINUADO"

@admin.register(ImagenInformacion)
class ImagenInformacionAdmin(admin.ModelAdmin):
    form = ImagenInformacionAdminForm

    list_display = ("id", "titulo", "orden", "activa", "imagen_link", "created_at", "updated_at")
    list_filter = ("activa",)
    search_fields = ("titulo", "descripcion")
    ordering = ("orden", "-updated_at")
    list_editable = ("orden", "activa")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Información principal", {
            "fields": ("titulo", "descripcion")
        }),
        ("Imagen", {
            "fields": ("imagen", "imagen_file")
        }),
        ("Configuración", {
            "fields": ("orden", "activa")
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def save_model(self, request, obj, form, change):
        imagen_file = form.cleaned_data.get("imagen_file")
        if imagen_file:
            obj.imagen = upload_product_image(imagen_file)
        super().save_model(request, obj, form, change)

    def imagen_link(self, obj):
        if not obj.imagen:
            return "-"
        return format_html('<a href="{}" target="_blank">Ver</a>', obj.imagen)

    imagen_link.short_description = "Imagen"

@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "accion", "modulo", "fecha", "descripcion")
    list_filter = ("accion", "modulo")
    search_fields = ("usuario__username", "accion", "modulo", "descripcion")
    ordering = ("-fecha",)