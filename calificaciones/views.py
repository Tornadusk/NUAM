from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


def check_staff_required(user):
    """Verifica si el usuario tiene permisos de staff (Administrador)"""
    return user.is_authenticated and user.is_staff


@login_required
def mantenedor_calificaciones(request):
    """Vista principal del Mantenedor de Calificaciones Tributarias"""
    # Agregar información de usuario al contexto para usar en template
    context = {
        'user': request.user,
        'is_admin': request.user.is_staff if request.user.is_authenticated else False
    }
    return render(request, 'calificaciones/mantenedor.html', context)
