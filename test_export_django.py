#!/usr/bin/env python
"""
Script que simula exactamente lo que hace Django al exportar
"""
import requests
import json
from datetime import datetime

# Simular el payload exacto que Django envía
def test_export_simulando_django(formato='csv'):
    """Simula exactamente lo que hace Django"""
    
    # Simular datos de calificaciones (como los que Django obtiene de la BD)
    lista_items = [
        {
            "columna1": "1",
            "columna2": "BTG Pactual",
            "columna3": "CL0001234567",
            "columna4": "publicada",
            "columna5": "2025",
            "columna6": "21/01/2025",
            "columna7": "Calificacion de ejemplo #1"
        },
        {
            "columna1": "2",
            "columna2": "Banco de Chile",
            "columna3": "COLBOND01",
            "columna4": "validada",
            "columna5": "2025",
            "columna6": "25/02/2025",
            "columna7": "Calificacion de ejemplo #2"
        }
    ]
    
    # Payload exacto como Django lo envía
    payload = {
        "titulo": "Reporte Maestro de Calificaciones",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "generado_por": "test_user",
        "formato": formato,
        "items": lista_items
    }
    
    print("=" * 60)
    print(f"SIMULANDO EXPORTACION DJANGO - Formato: {formato.upper()}")
    print("=" * 60)
    print(f"[EXPORT] [INFO] Intentando conectar con microservicio en http://localhost:5001/exportar para formato {formato}")
    print(f"[EXPORT] [INFO] Payload: {len(lista_items)} items, titulo: {payload['titulo']}")
    
    microservicio_disponible = False
    try:
        resp = requests.post("http://localhost:5001/exportar", json=payload, timeout=10)
        print(f"[EXPORT] Microservicio respondio con status {resp.status_code}")
        print(f"[EXPORT] Content-Type: {resp.headers.get('content-type', 'N/A')}")
        print(f"[EXPORT] Tamaño respuesta: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            if len(resp.content) == 0:
                print(f"[EXPORT] [ERROR] Microservicio respondio con 200 pero contenido vacio, usando fallback")
            else:
                microservicio_disponible = True
                
                if formato == 'pdf':
                    ext, mime = 'pdf', 'application/pdf'
                elif formato == 'csv':
                    ext, mime = 'csv', 'text/csv'
                elif formato == 'excel':
                    ext, mime = 'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                print(f"[EXPORT] [OK] Microservicio ACTIVO - Devolviendo archivo {formato} generado por microservicio (tamano: {len(resp.content)} bytes)")
                
                # Guardar archivo
                filename = f"test_django_export.{ext}"
                with open(filename, "wb") as f:
                    f.write(resp.content)
                print(f"[EXPORT] [OK] Archivo guardado como: {filename}")
                return True
        else:
            error_detail = ""
            try:
                error_detail = resp.text[:200]
            except:
                pass
            print(f"[EXPORT] [WARNING] Microservicio respondio con error HTTP {resp.status_code}: {error_detail}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"[EXPORT] [WARNING] Microservicio NO DISPONIBLE (conexion fallida): {str(e)}")
        print(f"[EXPORT] [WARNING] Usando fallback Django. Si el microservicio vuelve, se usara automaticamente en la proxima exportacion.")
        return False
    except requests.exceptions.Timeout as e:
        print(f"[EXPORT] [WARNING] Microservicio NO DISPONIBLE (timeout): {str(e)}")
        print(f"[EXPORT] [WARNING] Usando fallback Django. Si el microservicio vuelve, se usara automaticamente en la proxima exportacion.")
        return False
    except Exception as e:
        print(f"[EXPORT] [WARNING] Error inesperado: {type(e).__name__} - {str(e)}")
        return False
    
    if not microservicio_disponible:
        print(f"[EXPORT] [WARNING] Microservicio NO DISPONIBLE - Usando fallback Django para formato {formato}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRUEBA SIMULANDO COMPORTAMIENTO DE DJANGO")
    print("=" * 60)
    
    resultados = {
        'CSV': test_export_simulando_django('csv'),
        'Excel': test_export_simulando_django('excel'),
        'PDF': test_export_simulando_django('pdf')
    }
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for formato, resultado in resultados.items():
        status = "[OK] EXITOSO" if resultado else "[ERROR] FALLO"
        print(f"{formato:10} {status}")
    
    if all(resultados.values()):
        print("\n[OK] Todas las exportaciones funcionaron correctamente!")
        print("Si Django no funciona, el problema puede estar en:")
        print("  1. La codificacion de caracteres en Windows")
        print("  2. El servidor Django no esta ejecutandose")
        print("  3. El endpoint /calificaciones/exportar/<formato>/ no esta configurado correctamente")
    else:
        print("\n[WARNING] Algunas exportaciones fallaron. Revisa los errores arriba.")

