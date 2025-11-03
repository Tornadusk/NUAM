from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='/accounts/login/')
def home(request):
    """
    Vista principal del sistema.
    Muestra contenido diferenciado según el rol del usuario.
    """
    # Si el usuario es staff (admin), puede ver más opciones
    is_admin = request.user.is_staff if request.user.is_authenticated else False
    
    context = {
        'is_admin': is_admin,
        'username': request.user.username if request.user.is_authenticated else None
    }
    
    return render(request, 'index.html', context)

