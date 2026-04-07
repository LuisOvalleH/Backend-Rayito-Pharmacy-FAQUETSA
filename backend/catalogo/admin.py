from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Categoria, ImagenInformacion, SiteConfig
from .cloudinary_service import upload_product_image, ALLOWED_CONTENT_TYPES, MIN_DIMENSION


# ── Formularios ───────────────────────────────────────────────────────────────

class ImagenInformacionAdminForm(forms.ModelForm):
    imagen = forms.URLField(required=False, label="URL de imagen (opcional)")
    imagen_file = forms.ImageField(
        required=False,
        label="Subir imagen",
        help_text=f"JPG, PNG o WebP. Mínimo {MIN_DIMENSION}×{MIN_DIMENSION} px.",
    )

    class Meta:
        model = ImagenInformacion
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("imagen") and not cleaned.get("imagen_file"):
            raise forms.ValidationError("Debes proporcionar una URL o subir una imagen.")
        return cleaned

    def clean_imagen_file(self):
        archivo = self.cleaned_data.get("imagen_file")
        if not archivo:
            return archivo

        content_type = getattr(archivo, "content_type", "").lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError("Solo se permiten imágenes JPG, PNG o WebP.")

        try:
            from PIL import Image as PilImage
            archivo.seek(0)
            img = PilImage.open(archivo)
            w, h = img.size
            archivo.seek(0)
            if w < MIN_DIMENSION or h < MIN_DIMENSION:
                raise forms.ValidationError(
                    f"La imagen debe tener al menos {MIN_DIMENSION}×{MIN_DIMENSION} px "
                    f"(recibida: {w}×{h} px)."
                )
        except forms.ValidationError:
            raise
        except Exception:
            pass

        return archivo


# ── Admin: Categoria ──────────────────────────────────────────────────────────

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "slug")
    search_fields = ("nombre",)
    ordering = ("nombre",)
    readonly_fields = ("slug",)


# ── Admin: Producto ───────────────────────────────────────────────────────────

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "categoria",
        "estado_badge",
        "precio",
        "destacado",          # campo real, editable inline
        "imagen_link",
        "created_at",
        "updated_at",
    )
    list_filter = ("estado", "categoria", "destacado")
    search_fields = ("nombre", "descripcion", "categoria__nombre")
    ordering = ("-destacado", "-updated_at")
    list_editable = ("categoria", "precio", "destacado")

    fieldsets = (
        ("Información principal", {
            "fields": ("nombre", "descripcion", "categoria")
        }),
        ("Precio y estado", {
            "fields": ("precio", "estado", "destacado")
        }),
        ("Detalles farmacéuticos", {
            "fields": ("formula", "registro", "presentacion"),
            "classes": ("collapse",),
        }),
        ("Imagen", {
            "fields": ("imagen",)
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at")
        }),
    )
    readonly_fields = ("created_at", "updated_at")
    actions = (
        "marcar_disponible",
        "marcar_agotado",
        "marcar_descontinuado",
        "marcar_destacado",
        "quitar_destacado",
    )

    # ── Badges ────────────────────────────────────────────────────────

    def estado_badge(self, obj):
        est = (obj.estado or "").upper()
        if "DES" in est:
            bg, fg, label = "#FEE2E2", "#991B1B", "Descontinuado"
        elif "AGO" in est:
            bg, fg, label = "#FEF3C7", "#92400E", "Agotado"
        else:
            bg, fg, label = "#DCFCE7", "#166534", "Disponible"
        return format_html(
            '<span style="padding:4px 10px;border-radius:999px;'
            'background:{};color:{};font-weight:700;font-size:12px">{}</span>',
            bg, fg, label,
        )
    estado_badge.short_description = "Estado"
    estado_badge.admin_order_field = "estado"

    def destacado_badge(self, obj):
        if obj.destacado:
            return format_html(
                '<span style="padding:4px 10px;border-radius:999px;'
                'background:#FEF9C3;color:#854D0E;font-weight:700;font-size:12px">⭐ Destacado</span>'
            )
        return format_html('<span style="color:#9CA3AF;font-size:12px">—</span>')
    destacado_badge.short_description = "Destacado"
    destacado_badge.admin_order_field = "destacado"

    def imagen_link(self, obj):
        if not obj.imagen:
            return "—"
        return format_html('<a href="{}" target="_blank">Ver</a>', obj.imagen)
    imagen_link.short_description = "Imagen"

    # ── Acciones masivas ───────────────────────────────────────────────

    def marcar_disponible(self, request, queryset):
        queryset.update(estado=Producto.Estado.DISPONIBLE)
    marcar_disponible.short_description = "✔ Marcar como DISPONIBLE"

    def marcar_agotado(self, request, queryset):
        queryset.update(estado=Producto.Estado.AGOTADO)
    marcar_agotado.short_description = "✔ Marcar como AGOTADO"

    def marcar_descontinuado(self, request, queryset):
        queryset.update(estado=Producto.Estado.DESCONTINUADO)
    marcar_descontinuado.short_description = "✔ Marcar como DESCONTINUADO"

    def marcar_destacado(self, request, queryset):
        queryset.update(destacado=True)
    marcar_destacado.short_description = "⭐ Marcar como DESTACADO"

    def quitar_destacado(self, request, queryset):
        queryset.update(destacado=False)
    quitar_destacado.short_description = "✖ Quitar DESTACADO"


# ── Admin: ImagenInformacion ──────────────────────────────────────────────────

@admin.register(ImagenInformacion)
class ImagenInformacionAdmin(admin.ModelAdmin):
    form = ImagenInformacionAdminForm

    list_display = ("id", "titulo", "orden", "activa", "imagen_preview", "created_at")
    list_filter = ("activa",)
    search_fields = ("titulo", "descripcion")
    ordering = ("orden", "-updated_at")
    list_editable = ("orden", "activa")
    readonly_fields = ("created_at", "updated_at", "imagen_preview")

    fieldsets = (
        ("Información principal", {
            "fields": ("titulo", "descripcion")
        }),
        ("Imagen", {
            "fields": ("imagen", "imagen_file", "imagen_preview")
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

    def imagen_preview(self, obj):
        if not obj.imagen:
            return "—"
        return format_html(
            '<img src="{}" style="height:60px;border-radius:6px;object-fit:cover" />',
            obj.imagen,
        )
    imagen_preview.short_description = "Vista previa"

    def imagen_link(self, obj):
        if not obj.imagen:
            return "—"
        return format_html('<a href="{}" target="_blank">Ver</a>', obj.imagen)
    imagen_link.short_description = "Imagen"


# ── Admin: SiteConfig (singleton) ────────────────────────────────────────────

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """
    Muestra solo la instancia pk=1. El admin no puede crear ni eliminar,
    solo editar los valores de configuración.
    """
    fieldsets = (
        ("Catálogo público", {
            "description": "Controla cuántos productos se muestran en el catálogo.",
            "fields": ("productos_por_pagina",),
        }),
        ("Home", {
            "description": "Controla los elementos visibles en la página principal.",
            "fields": ("max_imagenes_home", "max_destacados_home"),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirige directamente al formulario de edición del singleton."""
        config = SiteConfig.get()
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(
            reverse("admin:catalogo_siteconfig_change", args=[config.pk])
        )
