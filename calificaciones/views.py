from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def mantenedor_calificaciones(request):
    """Vista principal del Mantenedor de Calificaciones Tributarias"""
    return render(request, 'calificaciones/mantenedor.html', {
        'user': request.user,
    })
