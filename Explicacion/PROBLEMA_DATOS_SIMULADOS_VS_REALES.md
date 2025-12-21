# Problema: Datos Simulados vs Datos Reales

## Situación Actual

Según la verificación:

### Datos REALES para hoy (2025-12-21):
- ✅ USD/CLP: 912.5789 - ExchangeRate API
- ✅ USD/PEN: 3.3668 - ExchangeRate API  
- ✅ USD/COP: 3858.3647 - ExchangeRate API

### Datos SIMULADOS para hoy (2025-12-21):
- 🔴 USD/CLP: 910.3848 - Datos Simulados
- 🔴 USD/PEN: 3.5986 - Datos Simulados
- 🔴 USD/COP: 4116.3758 - Datos Simulados

---

## Problema

El dashboard muestra los **datos simulados** porque se crearon después (ordenados por `vigente_desde` descendente).

Por eso ves valores simulados en lugar de los reales.

---

## Soluciones

### Opción 1: Eliminar datos simulados de hoy (Recomendado)

```bash
python eliminar_simulados_hoy.py
python manage.py obtener_tipos_cambio --forzar
```

Esto eliminará los simulados y actualizará los reales.

### Opción 2: Modificar la vista para priorizar datos reales

Modificar `api_tipos_cambio_por_pais()` para que muestre primero los datos reales (no simulados) cuando haya ambos.

### Opción 3: No generar datos simulados automáticamente

El problema es que los datos simulados se generaron con el botón "Cargar Datos Simulados". Si no los necesitas, simplemente no uses ese botón.

---

## Sobre el CLP/USD del 2025-12-15

El valor **-0.0151** parece incorrecto (no debería ser negativo). Puede ser:

1. **Error en el cálculo**: CLP/USD debería ser el inverso de USD/CLP
   - Si USD/CLP = 950.54, entonces CLP/USD = 1/950.54 ≈ 0.001052 (positivo)

2. **Dato corrupto**: Se guardó mal en algún momento

**Recomendación**: Este dato debería eliminarse o corregirse. Si no lo necesitas, puedes eliminarlo.

---

## Comandos Útiles

### Ver todos los datos para hoy

```python
python manage.py shell

>>> from microservicio.models import TipoCambio
>>> from django.utils import timezone
>>> hoy = timezone.now().date()
>>> 
>>> # Ver todos los datos de hoy
>>> for tc in TipoCambio.objects.filter(fecha=hoy).select_related('id_fuente').order_by('-vigente_desde'):
...     tipo = 'SIMULADO' if tc.id_fuente.codigo == 'SIMULADO' else 'REAL'
...     print(f"{tipo}: {tc.moneda_origen}/{tc.moneda_destino} = {tc.tasa} - {tc.id_fuente.nombre}")
```

### Eliminar solo datos simulados de hoy

```bash
python eliminar_simulados_hoy.py
```

### Obtener solo datos reales

```bash
python manage.py obtener_tipos_cambio --fuente EXCHANGERATE_API --forzar
```

---

## Resumen

✅ **Tienes datos reales** (3 registros de ExchangeRate API para hoy)  
⚠️ **El problema**: Los simulados aparecen primero porque son más recientes  
✅ **Solución**: Eliminar simulados y usar solo los reales


