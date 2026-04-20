# Análisis de Arquitectura — Backend Rayito Pharmacy

## Resumen del sistema

Backend Django REST API para una farmacia. Una sola app (`catalogo`) maneja todo: productos, categorías, imágenes, servicios, pasos de proceso y elementos de confianza. Autenticación JWT, imágenes en Cloudinary, email de contacto vía SMTP.

---

## Lo que está bien

### Configuración inteligente del entorno
El `settings.py` tiene una lógica de selección de base de datos en cascada (SQLite para tests → PostgreSQL por URL → PostgreSQL por variables → SQLite por defecto). Es limpio, facilita el onboarding local y el despliegue en producción sin tocar código.

### Seguridad base correcta
- JWT con tokens de acceso de 15 minutos — bien calibrado.
- Contraseñas hasheadas por el sistema de auth de Django.
- CORS configurado por variable de entorno, no hardcodeado.
- Protecciones XSS y clickjacking activas.
- Solo superusuarios pueden gestionar admins (`IsSuperAdmin`).

### Separación de responsabilidades
Serializers, views, permissions y el servicio de Cloudinary están en archivos propios. Para el tamaño actual del proyecto, es suficiente y está bien ordenado.

### Admin de Django bien aprovechado
Badges de color para el estado del producto, acciones bulk, vista previa de imágenes, edición inline. Esto le da valor real al panel sin código extra innecesario.

### Dependencias mínimas
Solo 7 paquetes. Sin bloat. Fácil de mantener y auditar.

---

## Problemas reales que hay que corregir

### 1. Permisos inconsistentes — CRÍTICO
`ServicioViewSet`, `PasoProcesoViewSet` y `ConfianzaViewSet` no definen ningún permiso. Cualquiera puede hacer `POST`, `PUT` o `DELETE` en esos endpoints sin autenticarse. Necesitan `get_permissions()` igual que `ProductoViewSet` y `CategoriaViewSet`.

```python
# Ejemplo del patrón que ya usas y deberías replicar:
def get_permissions(self):
    if self.action in ["list", "retrieve"]:
        return [AllowAny()]
    return [IsAdminUser()]
```

### 2. Sin paginación — ESCALABILIDAD
No hay clase de paginación configurada en `REST_FRAMEWORK`. Si la farmacia crece a miles de productos, el endpoint `GET /api/products/` devuelve todo de golpe. Agregar paginación es una línea:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

### 3. ContactoView sin límite de tasa — ABUSO
El endpoint `/api/contacto/` es público y envía emails reales. Sin rate limiting, cualquiera puede saturar el buzón o el servidor SMTP. Hay que agregar throttling:

```python
from rest_framework.throttling import AnonRateThrottle

class ContactoView(APIView):
    throttle_classes = [AnonRateThrottle]
```

Y en settings: `"DEFAULT_THROTTLE_RATES": {"anon": "10/hour"}`.

### 4. Sin tests — DEUDA TÉCNICA
`tests.py` está vacío. No hay cobertura de ningún endpoint ni de la lógica de permisos. Cualquier refactor es un salto de fe. Lo mínimo urgente son tests de permisos (que un anónimo no pueda crear/borrar productos) y del flujo de subida de imágenes.

### 5. Sin logging
No hay configuración de `LOGGING` en settings. En producción, los errores desaparecen en el vacío. Con Django es trivial enviar logs a un archivo o a stdout estructurado para que los capture el servidor.

---

## Puntos de mejora menores (no urgentes)

### Modelos simples sin timestamps
`Servicio`, `PasoProceso` y `Confianza` no tienen `created_at`/`updated_at`. No es bloqueante ahora, pero si algún día hay auditoría o versionado, hacer la migración con datos existentes es más complejo.

### `BLACKLIST_AFTER_ROTATION = False`
Los refresh tokens rotan pero no se invalidan tras la rotación. Si un token robado se usa antes que el legítimo, ambos son válidos por un momento. Activar la blacklist (`djangorestframework-simplejwt` lo soporta) cierra ese hueco.

### Emails de contacto síncronos
`ContactoView` envía el email en la misma request. Si el servidor SMTP tarda o falla, el usuario recibe un error 500. La solución robusta es Celery, pero mientras tanto al menos manejar el `SMTPException` y devolver un error 503 controlado en lugar de un crash.

### `STATIC_ROOT` no configurado
Sin `STATIC_ROOT`, `collectstatic` en producción no sabe dónde escribir. Añadir una línea evita sorpresas en el despliegue:

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

---

## Veredicto

La arquitectura **es sólida para el tamaño actual del proyecto**. La decisión de una sola app `catalogo` es correcta — dividir en múltiples apps tendría más overhead que beneficio dado el dominio tan cohesionado. El patrón de ViewSets + Router + Serializers está bien aplicado.

Los dos problemas que hay que resolver **antes de ir a producción con tráfico real**:
1. Los permisos faltantes en tres ViewSets.
2. El rate limiting en el endpoint de contacto.

El resto son mejoras de madurez que conviene ir incorporando iterativamente.
