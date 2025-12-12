"""
Vistas para Microservicio de Testing
Dashboard visual para ejecutar y visualizar tests desde la interfaz web
"""
import json
import subprocess
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .helpers import admin_required


@login_required
@admin_required
def testing_dashboard(request):
    """
    Vista principal para el dashboard de Testing
    Solo accesible para administradores
    """
    return render(request, 'microservicio/testing/dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_testing_status(request):
    """
    API: Obtiene el estado de los tests y configuración
    """
    try:
        # Verificar si pytest está disponible
        try:
            result = subprocess.run(['pytest', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5,
                                  cwd=settings.BASE_DIR)
            pytest_available = result.returncode == 0
            pytest_version = result.stdout.strip() if pytest_available else None
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pytest_available = False
            pytest_version = None
        
        # Verificar estructura de tests
        tests_dir = os.path.join(settings.BASE_DIR, 'tests')
        tests_exist = os.path.exists(tests_dir)
        
        # Contar archivos de test
        test_files_count = 0
        if tests_exist:
            for root, dirs, files in os.walk(tests_dir):
                test_files_count += len([f for f in files if f.startswith('test_') and f.endswith('.py')])
        
        return Response({
            'status': 'OK',
            'pytest_available': pytest_available,
            'pytest_version': pytest_version,
            'tests_directory_exists': tests_exist,
            'test_files_count': test_files_count,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_run_tests(request):
    """
    API: Ejecuta tests usando pytest
    Solo para administradores
    """
    if not request.user.is_staff:
        return Response({'error': 'Acceso denegado. Se requieren permisos de administrador.'}, status=403)
    
    try:
        test_path = request.data.get('test_path', 'tests/')
        verbose = request.data.get('verbose', False)
        coverage = request.data.get('coverage', False)
        
        # Construir comando pytest
        cmd = ['pytest', test_path]
        if verbose:
            cmd.append('-v')
        if coverage:
            cmd.append('--cov=.')
            cmd.append('--cov-report=json')
        
        # Ejecutar tests
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos máximo
            cwd=settings.BASE_DIR
        )
        
        # Parsear resultados
        output_lines = result.stdout.split('\n')
        summary = {}
        
        # Intentar extraer resumen de pytest
        for line in output_lines:
            if 'passed' in line or 'failed' in line or 'error' in line:
                # Formato típico: "X passed, Y failed in Z.XXs"
                summary['raw'] = line.strip()
        
        # Si hay coverage, intentar leer el archivo JSON
        coverage_data = None
        if coverage:
            coverage_file = os.path.join(settings.BASE_DIR, 'coverage.json')
            if os.path.exists(coverage_file):
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_full = json.load(f)
                        # Extraer solo los datos relevantes de coverage
                        if 'totals' in coverage_full:
                            coverage_data = {
                                'totals': coverage_full['totals']
                            }
                except Exception:
                    pass
        
        # Detectar errores comunes de Oracle
        error_hints = []
        error_text = (result.stderr or '') + (result.stdout or '')
        if 'ORA-01031' in error_text or 'privilegios insuficientes' in error_text:
            error_hints.append({
                'type': 'oracle_permissions',
                'title': '⚠️ Error de Permisos de Oracle (ORA-01031)',
                'message': 'El usuario de Oracle no tiene permisos suficientes para crear bases de datos de prueba.',
                'solution': 'SOLUCIÓN: El sistema está configurado para usar SQLite en tests automáticamente. Si ves este error, verifica que pytest_settings.py esté configurado correctamente. Consulta tests/README_ORACLE_TESTS.md para más detalles.',
                'details': 'Si necesitas usar Oracle en tests, consulta a tu DBA para obtener los permisos necesarios (CREATE DATABASE LINK, CREATE MATERIALIZED VIEW, etc.).'
            })
        
        return Response({
            'success': result.returncode == 0,
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'summary': summary,
            'coverage': coverage_data,
            'error_hints': error_hints,
            'timestamp': timezone.now().isoformat()
        })
    except subprocess.TimeoutExpired:
        return Response({'error': 'Los tests excedieron el tiempo límite de 5 minutos'}, status=408)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_test_list(request):
    """
    API: Lista los tests disponibles
    """
    try:
        tests_dir = os.path.join(settings.BASE_DIR, 'tests')
        if not os.path.exists(tests_dir):
            return Response({'tests': [], 'error': 'Directorio de tests no existe'})
        
        tests = []
        for root, dirs, files in os.walk(tests_dir):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    rel_path = os.path.relpath(os.path.join(root, file), settings.BASE_DIR)
                    # Intentar leer y extraer nombres de tests
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Buscar funciones de test
                            import re
                            test_functions = re.findall(r'def (test_\w+)', content)
                            tests.append({
                                'file': rel_path,
                                'test_functions': test_functions,
                                'test_count': len(test_functions)
                            })
                    except Exception:
                        tests.append({
                            'file': rel_path,
                            'test_functions': [],
                            'test_count': 0
                        })
        
        return Response({
            'tests': tests,
            'total_files': len(tests),
            'total_tests': sum(t['test_count'] for t in tests),
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

