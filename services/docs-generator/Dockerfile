FROM python:3.10-slim

# Instalar dependencias del sistema para WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    gobject-introspection \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY src/ ./src/

# Exponer puerto
EXPOSE 5000

# Comando de ejecución
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]