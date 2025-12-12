"""
Vistas principales del proyecto NUAM
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    """
    Vista principal (home) de NUAM
    """
    return render(request, 'index.html')
