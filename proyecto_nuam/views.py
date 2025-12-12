from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Pais
from corredoras.models import Corredora
from instrumentos.models import Instrumento
from calificaciones.models import Calificacion


@login_required(login_url='/accounts/login/')
def home(request):
    """
    Vista principal del sistema.
    Muestra contenido diferenciado según el rol del usuario.
    """
    # Si el usuario es staff (admin), puede ver más opciones
    is_admin = request.user.is_staff if request.user.is_authenticated else False
    
    # Obtener estadísticas dinámicas
    total_paises = Pais.objects.count()
    total_corredoras = Corredora.objects.filter(estado='activa').count()
    total_instrumentos = Instrumento.objects.count()
    total_calificaciones = Calificacion.objects.count()
    
    context = {
        'is_admin': is_admin,
        'username': request.user.username if request.user.is_authenticated else None,
        'total_paises': total_paises,
        'total_corredoras': total_corredoras,
        'total_instrumentos': total_instrumentos,
        'total_calificaciones': total_calificaciones,
    }
    
    return render(request, 'index.html', context)

