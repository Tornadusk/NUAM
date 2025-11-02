"""
Script para crear datos iniciales de ejemplo para el proyecto NUAM
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_nuam.settings')
django.setup()

from core.models import Pais, Moneda, MonedaPais, Mercado, Fuente
from corredoras.models import Corredora
from instrumentos.models import Instrumento
from calificaciones.models import FactorDef
from usuarios.models import Persona, Usuario, Rol, UsuarioRol, Colaborador

def create_data():
    print("=" * 60)
    print("CREANDO DATOS INICIALES PARA PROYECTO NUAM")
    print("=" * 60)
    
    # 1. Crear Países
    print("\n1. Creando Países...")
    paises_data = [
        {'codigo': 'CHL', 'nombre': 'Chile'},
        {'codigo': 'PER', 'nombre': 'Perú'},
        {'codigo': 'COL', 'nombre': 'Colombia'},
        {'codigo': 'USA', 'nombre': 'Estados Unidos'},
    ]
    
    paises = {}
    for pais_data in paises_data:
        pais, created = Pais.objects.get_or_create(**pais_data)
        paises[pais.codigo] = pais
        if created:
            print(f"  [OK] Pais creado: {pais.codigo} - {pais.nombre}")
        else:
            print(f"  [-] Pais ya existe: {pais.codigo} - {pais.nombre}")
    
    # 2. Crear Monedas
    print("\n2. Creando Monedas...")
    monedas_data = [
        {'codigo': 'CLP', 'nombre': 'Peso Chileno', 'decimales': 0, 'vigente': True},
        {'codigo': 'PEN', 'nombre': 'Sol Peruano', 'decimales': 2, 'vigente': True},
        {'codigo': 'COP', 'nombre': 'Peso Colombiano', 'decimales': 2, 'vigente': True},
        {'codigo': 'USD', 'nombre': 'Dólar Estadounidense', 'decimales': 2, 'vigente': True},
    ]
    
    monedas = {}
    for moneda_data in monedas_data:
        moneda, created = Moneda.objects.get_or_create(**moneda_data)
        monedas[moneda.codigo] = moneda
        if created:
            print(f"  [OK] Moneda creada: {moneda.codigo} - {moneda.nombre}")
        else:
            print(f"  [-] Moneda ya existe: {moneda.codigo} - {moneda.nombre}")
    
    # 2.1. Crear MonedaPais (relaciones moneda-país)
    print("\n2.1. Creando MonedaPais...")
    moneda_pais_data = [
        {'codigo_moneda': 'CLP', 'codigo_pais': 'CHL'},
        {'codigo_moneda': 'USD', 'codigo_pais': 'CHL'},
        {'codigo_moneda': 'PEN', 'codigo_pais': 'PER'},
        {'codigo_moneda': 'USD', 'codigo_pais': 'PER'},
        {'codigo_moneda': 'COP', 'codigo_pais': 'COL'},
        {'codigo_moneda': 'USD', 'codigo_pais': 'COL'},
    ]
    
    for mp_data in moneda_pais_data:
        moneda = monedas[mp_data['codigo_moneda']]
        pais = paises[mp_data['codigo_pais']]
        moneda_pais, created = MonedaPais.objects.get_or_create(
            id_moneda=moneda, 
            id_pais=pais,
            defaults={'vigente_desde': date.today()}
        )
        if created:
            print(f"  [OK] MonedaPais: {mp_data['codigo_moneda']} - {mp_data['codigo_pais']}")
    
    # 3. Crear Mercados
    print("\n3. Creando Mercados...")
    mercados_data = [
        {'codigo': 'BCS', 'nombre': 'Bolsa de Comercio de Santiago', 'id_pais': paises['CHL']},
        {'codigo': 'BVL', 'nombre': 'Bolsa de Valores de Lima', 'id_pais': paises['PER']},
        {'codigo': 'BVC', 'nombre': 'Bolsa de Valores de Colombia', 'id_pais': paises['COL']},
    ]
    
    mercados = {}
    for mercado_data in mercados_data:
        codigo = mercado_data['codigo']
        mercado_data_copy = mercado_data.copy()
        mercado, created = Mercado.objects.get_or_create(codigo=codigo, defaults=mercado_data_copy)
        mercados[codigo] = mercado
        if created:
            print(f"  [OK] Mercado creado: {mercado.codigo} - {mercado.nombre}")
        else:
            print(f"  [-] Mercado ya existe: {mercado.codigo} - {mercado.nombre}")
    
    # 4. Crear Fuentes
    print("\n4. Creando Fuentes...")
    fuentes_data = [
        {'codigo': 'SVS', 'nombre': 'Superintendencia de Valores y Seguros', 'descripcion': 'Fuente oficial chilena'},
        {'codigo': 'SMV', 'nombre': 'Superintendencia del Mercado de Valores', 'descripcion': 'Fuente oficial peruana'},
        {'codigo': 'SFC', 'nombre': 'Superintendencia Financiera de Colombia', 'descripcion': 'Fuente oficial colombiana'},
    ]
    
    fuentes = {}
    for fuente_data in fuentes_data:
        codigo = fuente_data['codigo']
        fuente_data_copy = fuente_data.copy()
        fuente, created = Fuente.objects.get_or_create(codigo=codigo, defaults=fuente_data_copy)
        fuentes[codigo] = fuente
        if created:
            print(f"  [OK] Fuente creada: {fuente.codigo} - {fuente.nombre}")
        else:
            print(f"  [-] Fuente ya existe: {fuente.codigo} - {fuente.nombre}")
    
    # 5. Crear Corredoras
    print("\n5. Creando Corredoras...")
    corredoras_data = [
        {'nombre': 'Banco de Chile', 'estado': 'activa', 'id_pais': paises['CHL']},
        {'nombre': 'Banco Santander', 'estado': 'activa', 'id_pais': paises['CHL']},
        {'nombre': 'Credicorp Capital', 'estado': 'activa', 'id_pais': paises['PER']},
        {'nombre': 'BTG Pactual', 'estado': 'activa', 'id_pais': paises['COL']},
    ]
    
    corredoras = []
    for corredora_data in corredoras_data:
        corredora, created = Corredora.objects.get_or_create(nombre=corredora_data['nombre'], defaults=corredora_data)
        corredoras.append(corredora)
        if created:
            print(f"  [OK] Corredora creada: {corredora.nombre}")
        else:
            print(f"  [-] Corredora ya existe: {corredora.nombre}")
    
    # 6. Crear Roles
    print("\n6. Creando Roles...")
    roles_data = [
        {'nombre': 'Administrador'},
        {'nombre': 'Operador'},
        {'nombre': 'Analista'},
        {'nombre': 'Consultor'},
        {'nombre': 'Auditor'},
    ]
    
    roles = {}
    for rol_data in roles_data:
        rol, created = Rol.objects.get_or_create(**rol_data)
        roles[rol.nombre] = rol
        if created:
            print(f"  [OK] Rol creado: {rol.nombre}")
        else:
            print(f"  [-] Rol ya existe: {rol.nombre}")
    
    # 7. Crear Factores F08-F37
    print("\n7. Creando Factores F08-F37...")
    factores_data = [
        {'codigo_factor': 'F08', 'nombre_corto': 'Factor-08', 'tipo_valor': 'factor', 'orden_visual': 1},
        {'codigo_factor': 'F09', 'nombre_corto': 'Factor-09', 'tipo_valor': 'factor', 'orden_visual': 2},
        {'codigo_factor': 'F10', 'nombre_corto': 'Factor-10', 'tipo_valor': 'factor', 'orden_visual': 3},
        {'codigo_factor': 'F11', 'nombre_corto': 'Factor-11', 'tipo_valor': 'factor', 'orden_visual': 4},
        {'codigo_factor': 'F12', 'nombre_corto': 'Factor-12', 'tipo_valor': 'factor', 'orden_visual': 5},
        {'codigo_factor': 'F13', 'nombre_corto': 'Factor-13', 'tipo_valor': 'factor', 'orden_visual': 6},
        {'codigo_factor': 'F14', 'nombre_corto': 'Factor-14', 'tipo_valor': 'factor', 'orden_visual': 7},
        {'codigo_factor': 'F15', 'nombre_corto': 'Factor-15', 'tipo_valor': 'factor', 'orden_visual': 8},
        {'codigo_factor': 'F16', 'nombre_corto': 'Factor-16', 'tipo_valor': 'factor', 'orden_visual': 9},
        {'codigo_factor': 'F17', 'nombre_corto': 'Factor-17', 'tipo_valor': 'factor', 'orden_visual': 10},
        {'codigo_factor': 'F18', 'nombre_corto': 'Factor-18', 'tipo_valor': 'factor', 'orden_visual': 11},
        {'codigo_factor': 'F19A', 'nombre_corto': 'Factor-19A', 'tipo_valor': 'factor', 'orden_visual': 12},
        {'codigo_factor': 'F20', 'nombre_corto': 'Factor-20', 'tipo_valor': 'factor', 'orden_visual': 13},
        {'codigo_factor': 'F21', 'nombre_corto': 'Factor-21', 'tipo_valor': 'factor', 'orden_visual': 14},
        {'codigo_factor': 'F22', 'nombre_corto': 'Factor-22', 'tipo_valor': 'factor', 'orden_visual': 15},
        {'codigo_factor': 'F23', 'nombre_corto': 'Factor-23', 'tipo_valor': 'factor', 'orden_visual': 16},
        {'codigo_factor': 'F24', 'nombre_corto': 'Factor-24', 'tipo_valor': 'factor', 'orden_visual': 17},
        {'codigo_factor': 'F25', 'nombre_corto': 'Factor-25', 'tipo_valor': 'factor', 'orden_visual': 18},
        {'codigo_factor': 'F26', 'nombre_corto': 'Factor-26', 'tipo_valor': 'factor', 'orden_visual': 19},
        {'codigo_factor': 'F27', 'nombre_corto': 'Factor-27', 'tipo_valor': 'factor', 'orden_visual': 20},
        {'codigo_factor': 'F28', 'nombre_corto': 'Factor-28', 'tipo_valor': 'factor', 'orden_visual': 21},
        {'codigo_factor': 'F29', 'nombre_corto': 'Factor-29', 'tipo_valor': 'factor', 'orden_visual': 22},
        {'codigo_factor': 'F30', 'nombre_corto': 'Factor-30', 'tipo_valor': 'factor', 'orden_visual': 23},
        {'codigo_factor': 'F31', 'nombre_corto': 'Factor-31', 'tipo_valor': 'factor', 'orden_visual': 24},
        {'codigo_factor': 'F32', 'nombre_corto': 'Factor-32', 'tipo_valor': 'factor', 'orden_visual': 25},
        {'codigo_factor': 'F33', 'nombre_corto': 'Factor-33', 'tipo_valor': 'factor', 'orden_visual': 26},
        {'codigo_factor': 'F34', 'nombre_corto': 'Factor-34', 'tipo_valor': 'factor', 'orden_visual': 27},
        {'codigo_factor': 'F35', 'nombre_corto': 'Factor-35', 'tipo_valor': 'factor', 'orden_visual': 28},
        {'codigo_factor': 'F36', 'nombre_corto': 'Factor-36', 'tipo_valor': 'factor', 'orden_visual': 29},
        {'codigo_factor': 'F37', 'nombre_corto': 'Factor-37', 'tipo_valor': 'factor', 'orden_visual': 30},
    ]
    
    factores = {}
    for factor_data in factores_data:
        codigo = factor_data['codigo_factor']
        factor, created = FactorDef.objects.get_or_create(codigo_factor=codigo, defaults=factor_data)
        factores[codigo] = factor
        if created:
            print(f"  [OK] Factor creado: {factor.codigo_factor} - {factor.nombre_corto}")
    
    # 8. Crear Usuarios de ejemplo
    print("\n8. Creando Usuarios de ejemplo...")
    
    # 8.1 Admin
    try:
        persona_admin = Persona.objects.get_or_create(
            primer_nombre='Admin',
            apellido_paterno='Sistema',
            defaults={
                'segundo_nombre': 'NUAM',
                'apellido_materno': '',
                'fecha_nacimiento': date(1990, 1, 1),
                'genero': 'Masculino',
                'nacionalidad': 'CHL'
            }
        )[0]
        
        usuario_admin = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'id_persona': persona_admin,
                'estado': 'activo'
            }
        )[0]
        usuario_admin.set_password('admin123')
        usuario_admin.save()
        
        # Asignar rol Administrador
        UsuarioRol.objects.get_or_create(
            id_usuario=usuario_admin,
            id_rol=roles['Administrador']
        )
        
        # Crear colaborador
        Colaborador.objects.get_or_create(
            id_usuario=usuario_admin,
            defaults={'gmail': 'admin@nuam.cl'}
        )
        
        print("  [OK] Usuario admin creado")
    except Exception as e:
        print(f"  [-] Usuario admin ya existe: {e}")
    
    # 8.2 Operador
    try:
        persona_operador = Persona.objects.get_or_create(
            primer_nombre='Operador',
            apellido_paterno='Demo',
            defaults={
                'segundo_nombre': 'Test',
                'apellido_materno': '',
                'fecha_nacimiento': date(1995, 5, 15),
                'genero': 'Femenino',
                'nacionalidad': 'CHL'
            }
        )[0]
        
        usuario_operador = Usuario.objects.get_or_create(
            username='operador',
            defaults={
                'id_persona': persona_operador,
                'estado': 'activo'
            }
        )[0]
        usuario_operador.set_password('op123456')
        usuario_operador.save()
        
        # Asignar rol Operador
        UsuarioRol.objects.get_or_create(
            id_usuario=usuario_operador,
            id_rol=roles['Operador']
        )
        
        # Crear colaborador
        Colaborador.objects.get_or_create(
            id_usuario=usuario_operador,
            defaults={'gmail': 'operador@nuam.cl'}
        )
        
        print("  [OK] Usuario operador creado")
    except Exception as e:
        print(f"  [-] Usuario operador ya existe: {e}")
    
    # 9. Crear Instrumentos de ejemplo
    print("\n9. Creando Instrumentos de ejemplo...")
    instrumentos_data = [
        {'codigo': 'CL0001234567', 'nombre': 'ADP Bolsa', 'tipo': 'Acción', 'emisor': 'Empresa Demo', 'id_mercado': mercados['BCS'], 'id_moneda': monedas['CLP']},
        {'codigo': 'PEFIX01', 'nombre': 'Bono Peruano', 'tipo': 'Bonos', 'emisor': 'Gobierno Peruano', 'id_mercado': mercados['BVL'], 'id_moneda': monedas['PEN']},
    ]
    
    instrumentos = []
    for inst_data in instrumentos_data:
        instrumento, created = Instrumento.objects.get_or_create(codigo=inst_data['codigo'], defaults=inst_data)
        instrumentos.append(instrumento)
        if created:
            print(f"  [OK] Instrumento creado: {instrumento.codigo}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("DATOS INICIALES CREADOS EXITOSAMENTE")
    print("=" * 60)
    print("\nResumen:")
    print(f"  - Países: {Pais.objects.count()}")
    print(f"  - Monedas: {Moneda.objects.count()}")
    print(f"  - MonedaPais: {MonedaPais.objects.count()}")
    print(f"  - Mercados: {Mercado.objects.count()}")
    print(f"  - Fuentes: {Fuente.objects.count()}")
    print(f"  - Corredoras: {Corredora.objects.count()}")
    print(f"  - Roles: {Rol.objects.count()}")
    print(f"  - Factores: {FactorDef.objects.count()}")
    print(f"  - Usuarios: {Usuario.objects.count()}")
    print(f"  - Instrumentos: {Instrumento.objects.count()}")
    print("\nPara ver los datos, accede a: http://127.0.0.1:8000/admin/")
    print("\nCredenciales de acceso:")
    print("  Usuario: admin / Contraseña: admin123")
    print("  Usuario: operador / Contraseña: op123456")

if __name__ == '__main__':
    create_data()
