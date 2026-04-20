def registrar_historial(usuario, accion, modulo, descripcion):
    from .models import Historial
    Historial.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        descripcion=descripcion
    )