#!/usr/bin/env python
"""
Script de prueba para verificar que el microservicio de documentos funciona correctamente
"""
import requests
import json
from datetime import datetime

# Configuración
MICROSERVICIO_URL = "http://localhost:5001"
ENDPOINT_EXPORTAR = f"{MICROSERVICIO_URL}/exportar"
ENDPOINT_HEALTH = f"{MICROSERVICIO_URL}/health"

def test_health():
    """Probar el endpoint de health"""
    print("=" * 60)
    print("1. Probando endpoint /health")
    print("=" * 60)
    try:
        resp = requests.get(ENDPOINT_HEALTH, timeout=5)
        print(f"[OK] Status: {resp.status_code}")
        print(f"[OK] Respuesta: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_exportar_csv():
    """Probar exportación CSV"""
    print("\n" + "=" * 60)
    print("2. Probando exportación CSV")
    print("=" * 60)
    
    payload = {
        "titulo": "Reporte Maestro de Calificaciones",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "generado_por": "test_user",
        "formato": "csv",
        "items": [
            {
                "columna1": "1",
                "columna2": "BTG Pactual",
                "columna3": "CL0001234567",
                "columna4": "publicada",
                "columna5": "2025",
                "columna6": "21/01/2025",
                "columna7": "Calificación de ejemplo #1"
            },
            {
                "columna1": "2",
                "columna2": "Banco de Chile",
                "columna3": "COLBOND01",
                "columna4": "validada",
                "columna5": "2025",
                "columna6": "25/02/2025",
                "columna7": "Calificación de ejemplo #2"
            }
        ]
    }
    
    try:
        print(f"[INFO] Enviando peticion a {ENDPOINT_EXPORTAR}")
        print(f"[INFO] Payload: {len(payload['items'])} items")
        
        resp = requests.post(ENDPOINT_EXPORTAR, json=payload, timeout=10)
        
        print(f"[INFO] Status: {resp.status_code}")
        print(f"[INFO] Content-Type: {resp.headers.get('content-type', 'N/A')}")
        print(f"[INFO] Tamano respuesta: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            print("[OK] CSV generado exitosamente")
            # Guardar archivo de prueba
            with open("test_export.csv", "wb") as f:
                f.write(resp.content)
            print("[OK] Archivo guardado como: test_export.csv")
            return True
        else:
            print(f"[ERROR] Error HTTP {resp.status_code}")
            try:
                print(f"[ERROR] Detalle: {resp.json()}")
            except:
                print(f"[ERROR] Respuesta: {resp.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Error de conexion: {e}")
        print("[WARNING] El microservicio no esta disponible en http://localhost:5001")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_exportar_excel():
    """Probar exportación Excel"""
    print("\n" + "=" * 60)
    print("3. Probando exportación Excel")
    print("=" * 60)
    
    payload = {
        "titulo": "Reporte Maestro de Calificaciones",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "generado_por": "test_user",
        "formato": "excel",
        "items": [
            {
                "columna1": "1",
                "columna2": "BTG Pactual",
                "columna3": "CL0001234567",
                "columna4": "publicada",
                "columna5": "2025",
                "columna6": "21/01/2025",
                "columna7": "Calificación de ejemplo #1"
            }
        ]
    }
    
    try:
        print(f"[INFO] Enviando peticion a {ENDPOINT_EXPORTAR}")
        resp = requests.post(ENDPOINT_EXPORTAR, json=payload, timeout=10)
        
        print(f"[INFO] Status: {resp.status_code}")
        print(f"[INFO] Content-Type: {resp.headers.get('content-type', 'N/A')}")
        print(f"[INFO] Tamano respuesta: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            print("[OK] Excel generado exitosamente")
            with open("test_export.xlsx", "wb") as f:
                f.write(resp.content)
            print("[OK] Archivo guardado como: test_export.xlsx")
            return True
        else:
            print(f"[ERROR] Error HTTP {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_exportar_pdf():
    """Probar exportación PDF"""
    print("\n" + "=" * 60)
    print("4. Probando exportación PDF")
    print("=" * 60)
    
    payload = {
        "titulo": "Reporte Maestro de Calificaciones",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "generado_por": "test_user",
        "formato": "pdf",
        "items": [
            {
                "columna1": "1",
                "columna2": "BTG Pactual",
                "columna3": "CL0001234567",
                "columna4": "publicada",
                "columna5": "2025",
                "columna6": "21/01/2025",
                "columna7": "Calificación de ejemplo #1"
            }
        ]
    }
    
    try:
        print(f"[INFO] Enviando peticion a {ENDPOINT_EXPORTAR}")
        resp = requests.post(ENDPOINT_EXPORTAR, json=payload, timeout=10)
        
        print(f"[INFO] Status: {resp.status_code}")
        print(f"[INFO] Content-Type: {resp.headers.get('content-type', 'N/A')}")
        print(f"[INFO] Tamano respuesta: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            print("[OK] PDF generado exitosamente")
            with open("test_export.pdf", "wb") as f:
                f.write(resp.content)
            print("[OK] Archivo guardado como: test_export.pdf")
            return True
        else:
            print(f"[ERROR] Error HTTP {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "=" * 60)
    print("PRUEBAS DEL MICROSERVICIO DE DOCUMENTOS")
    print("=" * 60)
    
    results = {
        "health": test_health(),
        "csv": test_exportar_csv(),
        "excel": test_exportar_excel(),
        "pdf": test_exportar_pdf()
    }
    
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    for test, result in results.items():
        status = "[OK] PASS" if result else "[ERROR] FAIL"
        print(f"{test.upper():15} {status}")
    
    total = sum(results.values())
    print(f"\nTotal: {total}/{len(results)} pruebas pasaron")
    
    if all(results.values()):
        print("\n[OK] Todas las pruebas pasaron! El microservicio esta funcionando correctamente.")
    else:
        print("\n[WARNING] Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()

