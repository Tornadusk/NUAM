"""
Generador de gráficos usando matplotlib
Convierte configuraciones de Chart.js a imágenes PNG/JPG
"""
import io
import base64
from typing import List, Dict, Optional, Literal
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from PIL import Image


# Colores predefinidos similares a Chart.js
COLORS = [
    '#667EEA',  # rgb(102, 126, 234)
    '#FF3333',  # rgb(255, 51, 51)
    '#198754',  # rgb(25, 135, 84)
    '#FFC107',  # rgb(255, 193, 7)
    '#DC3545',  # rgb(220, 53, 69)
    '#0DCAF0',  # rgb(13, 202, 240)
    '#6610F2',  # rgb(102, 16, 242)
    '#E91E63',  # rgb(233, 30, 99)
]


def hex_to_rgb(hex_color: str) -> tuple:
    """Convierte color hex a RGB (0-1)"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def parse_color(color: str) -> tuple:
    """Parsea color desde formato RGB/RGBA/hex a RGB (0-1)"""
    if not color:
        return (0.4, 0.5, 0.9)  # Default azul
    
    color = color.strip()
    
    # RGB/RGBA: rgb(102, 126, 234) o rgba(102, 126, 234, 0.1)
    if color.startswith('rgb'):
        # Extraer números
        import re
        numbers = re.findall(r'\d+\.?\d*', color)
        if len(numbers) >= 3:
            return (float(numbers[0])/255.0, float(numbers[1])/255.0, float(numbers[2])/255.0)
    
    # Hex: #667EEA
    if color.startswith('#'):
        return hex_to_rgb(color)
    
    # Color name (básico)
    color_map = {
        'blue': (0.4, 0.5, 0.9),
        'red': (1.0, 0.2, 0.2),
        'green': (0.1, 0.5, 0.3),
        'yellow': (1.0, 0.76, 0.03),
    }
    return color_map.get(color.lower(), (0.4, 0.5, 0.9))


def generar_grafico_imagen(
    labels: List[str],
    datasets: List[Dict],
    chart_type: str = "line",
    titulo: str = None,
    x_label: str = None,
    y_label: str = None,
    width: int = 1200,
    height: int = 600,
    formato: str = "png",
    calidad: int = 95
) -> bytes:
    """
    Genera una imagen del gráfico
    
    Args:
        labels: Lista de etiquetas del eje X
        datasets: Lista de datasets (compatible con Chart.js)
        chart_type: Tipo de gráfico (line, bar, radar)
        titulo: Título del gráfico
        x_label: Etiqueta del eje X
        y_label: Etiqueta del eje Y
        width: Ancho en pixels
        height: Alto en pixels
        formato: Formato de salida (png, jpg)
        calidad: Calidad para JPG (1-100)
    
    Returns:
        Bytes de la imagen
    """
    # Normalizar chart_type para asegurar comparaciones correctas
    chart_type_original = chart_type
    chart_type = str(chart_type).strip().lower() if chart_type else 'line'
    
    # DEBUG: Verificar que chart_type sea el correcto
    # Si chart_type no es válido, usar 'line'
    if chart_type not in ['line', 'bar', 'radar']:
        chart_type = 'line'
    
    # DEBUG: Forzar que se vea el chart_type que se está usando
    print(f"CHART_GENERATOR_DEBUG: chart_type recibido='{chart_type_original}', normalizado='{chart_type}'", flush=True)
    
    # Validar que todos los datasets tengan la misma longitud que labels
    num_labels = len(labels)
    if num_labels == 0:
        raise ValueError("No se proporcionaron labels para el gráfico")
    
    # Manejar gráfico radar de forma especial (usa proyección polar)
    if chart_type == 'radar':
        # Para radar, necesitamos crear el plot con proyección polar
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100, subplot_kw=dict(projection='polar'))
        fig.patch.set_facecolor('#ffffff')
        
        # Calcular ángulos para los labels
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]  # Cerrar el círculo
        
        # Procesar cada dataset para radar
        for idx, dataset in enumerate(datasets):
            label = dataset.get('label', f'Serie {idx+1}')
            data = dataset.get('data', [])
            
            if not data or len(data) == 0:
                continue
            
            # Asegurar que los datos tengan la misma longitud que los labels
            if len(data) < len(labels):
                last_value = data[-1] if len(data) > 0 else 0
                data = list(data) + [last_value] * (len(labels) - len(data))
            elif len(data) > len(labels):
                data = data[:len(labels)]
            
            data_array = np.array(data, dtype=float)
            data_array = np.concatenate((data_array, [data_array[0]]))  # Cerrar el círculo
            
            border_color = dataset.get('borderColor', COLORS[idx % len(COLORS)])
            bg_color = dataset.get('backgroundColor', border_color)
            border_rgb = parse_color(border_color)
            bg_rgb = parse_color(bg_color)
            
            ax.plot(angles, data_array, 'o-', linewidth=2, label=label, color=border_rgb)
            ax.fill(angles, data_array, alpha=0.25, color=bg_rgb)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_ylim(0, None)
        ax.grid(True)
        
        if len(datasets) > 1:
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        if titulo:
            fig.suptitle(titulo, fontsize=16, fontweight='bold', y=0.98)
        
        # Guardar a bytes para radar
        if formato.lower() == 'jpg' or formato.lower() == 'jpeg':
            buf_png = io.BytesIO()
            fig.savefig(buf_png, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buf_png.seek(0)
            
            try:
                img = Image.open(buf_png)
                if img.mode in ('RGBA', 'LA', 'P'):
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    elif img.mode == 'LA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        la_rgba = img.convert('RGBA')
                        background.paste(la_rgba, mask=la_rgba.split()[3])
                        img = background
                    elif img.mode == 'P':
                        if 'transparency' in img.info:
                            img = img.convert('RGBA')
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[3])
                            img = background
                        else:
                            img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                buf_jpg = io.BytesIO()
                img.save(buf_jpg, format='JPEG', quality=min(max(calidad, 1), 100), optimize=True)
                buf_jpg.seek(0)
                result = buf_jpg.read()
                buf_jpg.close()
            except Exception as e:
                raise ValueError(f"Error al convertir imagen a JPEG: {str(e)}")
            finally:
                buf_png.close()
                plt.close(fig)
            
            return result
        else:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            result = buf.read()
            buf.close()
            return result
    
    # Para line y bar, usar configuración normal
    # Configurar figura
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    fig.patch.set_facecolor('#ffffff')
    
    # Procesar datasets
    for idx, dataset in enumerate(datasets):
        label = dataset.get('label', f'Serie {idx+1}')
        data = dataset.get('data', [])
        
        if not data:
            continue
        
        # Asegurar que los datos tengan la misma longitud que los labels
        # Si hay menos datos, rellenar con el último valor (mejor que None)
        # Si hay más datos, truncar
        if len(data) < num_labels:
            # Rellenar con el último valor conocido para mantener continuidad
            last_value = data[-1] if len(data) > 0 else 0
            data = list(data) + [last_value] * (num_labels - len(data))
        elif len(data) > num_labels:
            # Truncar datos extras
            data = data[:num_labels]
        
        # Convertir a numpy array para facilitar el manejo
        data_array = np.array(data, dtype=float)
        
        # Obtener colores
        border_color = dataset.get('borderColor', COLORS[idx % len(COLORS)])
        bg_color = dataset.get('backgroundColor', border_color)
        
        border_rgb = parse_color(border_color)
        bg_rgb = parse_color(bg_color)
        
        # Ajustar transparencia para fill
        fill_alpha = 0.1 if chart_type == 'line' else 0.7
        
        # DEBUG: Ver qué tipo de gráfico se está dibujando
        print(f"CHART_GENERATOR_DEBUG: Dibujando dataset {idx}, chart_type='{chart_type}'", flush=True)
        
        # Generar gráfico según el tipo
        x_pos = np.arange(len(data_array))
        
        if chart_type == 'line':
            # Gráfico de línea
            ax.plot(x_pos, data_array, label=label, color=border_rgb, linewidth=2, alpha=0.9, marker='o', markersize=4)
            if dataset.get('fill', False):
                ax.fill_between(x_pos, data_array, alpha=fill_alpha, color=bg_rgb)
        elif chart_type == 'bar':
            # Gráfico de barras
            bar_width = 0.8 / len(datasets) if len(datasets) > 1 else 0.6
            offset = (idx - len(datasets)/2 + 0.5) * bar_width
            ax.bar(
                x_pos + offset,
                data_array,
                width=bar_width,
                label=label,
                color=bg_rgb,
                alpha=0.8,
                edgecolor=border_rgb,
                linewidth=1.5
            )
        else:
            # Fallback a línea
            ax.plot(x_pos, data_array, label=label, color=border_rgb, linewidth=2, alpha=0.9, marker='o', markersize=4)
        
        # CÓDIGO ORIGINAL COMENTADO PARA PRUEBA:
        # if chart_type == 'line':
        #     # Gráfico de línea
        #     print(f"CHART_GENERATOR_DEBUG: Usando ax.plot para línea", flush=True)
        #     x_pos = np.arange(len(data_array))
        #     ax.plot(x_pos, data_array, label=label, color=border_rgb, linewidth=2, alpha=0.9, marker='o', markersize=4)
        #     
        #     # Fill si está habilitado
        #     if dataset.get('fill', False):
        #         ax.fill_between(x_pos, data_array, alpha=fill_alpha, color=bg_rgb)
        # 
        # elif chart_type == 'bar':
        #     # Gráfico de barras
        #     print(f"CHART_GENERATOR_DEBUG: Usando ax.bar para barras", flush=True)
        #     x_pos = np.arange(len(data_array))
        #     bar_width = 0.8 / len(datasets) if len(datasets) > 1 else 0.6
        #     offset = (idx - len(datasets)/2 + 0.5) * bar_width
        #     ax.bar(
        #         x_pos + offset,
        #         data_array,
        #         width=bar_width,
        #         label=label,
        #         color=bg_rgb,
        #         alpha=0.8,
        #         edgecolor=border_rgb,
        #         linewidth=1.5
        #     )
        # else:
        #     # Fallback a línea si no es ni line ni bar ni radar (radar ya se maneja antes)
        #     print(f"CHART_GENERATOR_DEBUG: Tipo desconocido '{chart_type}', usando línea como fallback", flush=True)
        #     x_pos = np.arange(len(data_array))
        #     ax.plot(x_pos, data_array, label=label, color=border_rgb, linewidth=2, alpha=0.9, marker='o', markersize=4)
        
    
    # Configurar ejes y estilo (para line y bar)
    ax.set_xlabel(x_label or '', fontsize=12)
    ax.set_ylabel(y_label or '', fontsize=12)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#ffffff')
    
    if titulo:
        fig.suptitle(titulo, fontsize=16, fontweight='bold', y=0.98)
    
    # Leyenda
    if len(datasets) > 1:
        ax.legend(loc='best', framealpha=0.9)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar a bytes
    try:
        if formato.lower() == 'jpg' or formato.lower() == 'jpeg':
            # Para JPG, guardar primero como PNG y luego convertir a JPEG con calidad usando Pillow
            # porque matplotlib Agg no soporta el parámetro quality directamente
            buf_png = io.BytesIO()
            fig.savefig(buf_png, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buf_png.seek(0)
            
            # Convertir PNG a JPEG con calidad usando Pillow
            try:
                img = Image.open(buf_png)
                # Convertir a RGB si tiene transparencia (RGBA, LA, P)
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # mask es el canal alpha (índice 3)
                    img = background
                elif img.mode == 'LA':
                    # LA mode: L (luminance) + A (alpha)
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    # Convertir LA a RGBA primero para poder usar el alpha como mask
                    la_rgba = img.convert('RGBA')
                    background.paste(la_rgba, mask=la_rgba.split()[3])
                    img = background
                elif img.mode == 'P':
                    # Paleta mode: convertir a RGB (puede tener transparencia)
                    if 'transparency' in img.info:
                        img = img.convert('RGBA')
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    else:
                        img = img.convert('RGB')
                elif img.mode != 'RGB':
                    # Cualquier otro modo, convertir a RGB directamente
                    img = img.convert('RGB')
                
                buf_jpg = io.BytesIO()
                img.save(buf_jpg, format='JPEG', quality=min(max(calidad, 1), 100), optimize=True)
                buf_jpg.seek(0)
                result = buf_jpg.read()
                buf_jpg.close()
            except Exception as e:
                raise ValueError(f"Error al convertir imagen a JPEG: {str(e)}")
            finally:
                buf_png.close()
                plt.close(fig)
            
            if not result:
                raise ValueError("No se pudo generar la imagen JPEG")
            
            return result
        else:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            result = buf.read()
            buf.close()
            
            if not result:
                raise ValueError("No se pudo generar la imagen PNG")
            
            return result
    except Exception as e:
        plt.close(fig)
        raise


def generar_grafico_desde_config(config: Dict) -> bytes:
    """
    Genera gráfico desde una configuración completa (compatible con ChartConfig)
    """
    chart_config = config.get('chartConfig', config)
    
    labels = chart_config.get('labels', [])
    datasets_raw = chart_config.get('datasets', [])
    chart_type = chart_config.get('type', 'line')
    titulo = chart_config.get('title', chart_config.get('titulo'))
    x_label = chart_config.get('xLabel', chart_config.get('x_label'))
    y_label = chart_config.get('yLabel', chart_config.get('y_label'))
    width = chart_config.get('width', 1200)
    height = chart_config.get('height', 600)
    formato = config.get('format', config.get('formato', 'png'))
    calidad = config.get('quality', 95)
    
    return generar_grafico_imagen(
        labels=labels,
        datasets=datasets_raw,
        chart_type=chart_type,
        titulo=titulo,
        x_label=x_label,
        y_label=y_label,
        width=width,
        height=height,
        formato=formato,
        calidad=calidad
    )

