from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Categoria


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
