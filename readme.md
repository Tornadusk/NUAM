

## Instalación

0. **Preparar carpeta y terminal**
   - Windows:
     - Crea una carpeta genérica, por ejemplo: `C:\Proyectos`.
     - Abre CMD/PowerShell y muévete a esa carpeta:
       ```bash
       cd "C:\Proyectos"
       ```
     - Explicado simple: una "carpeta" es un lugar donde guardarás el proyecto. Abre el menú inicio, escribe "cmd" y presiona Enter. Se abrirá una ventana negra (la terminal). Escribe el comando de arriba tal cual y pulsa Enter. Si no existe la carpeta, créala antes en el Explorador.
     - Comprobar que estás dentro: escribe `dir` y pulsa Enter. Verás el listado de archivos de esa carpeta.
   - Linux/Mac:
     - Crea y entra a un directorio de trabajo estándar, por ejemplo `~/projects`:
       ```bash
       mkdir -p ~/projects && cd ~/projects
       ```
     - Explicado simple: abre la aplicación "Terminal". Copia y pega la línea de arriba y pulsa Enter. Crea (si no existe) y entra en una carpeta llamada `projects` dentro de tu carpeta personal.
     - Comprobar que estás dentro: escribe `ls` y pulsa Enter. Verás el listado de archivos de esa carpeta.

   - Si usas Ubuntu/Debian y no tienes Git/Python instalados, ejecútalo primero:
     ```bash
     sudo apt update
     sudo apt install -y git python3 python3-venv python3-pip
     ```

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Tornadusk/NUAM.git
   cd django-retos-logicos
   ```

   Si no tienes Git, tienes dos alternativas:

   - Alternativa A (sin Git): Descargar ZIP
     1) Abre el repo: https://github.com/Tornadusk/NUAM
     2) Botón "Code" → "Download ZIP"
     3) Descomprime el ZIP en tu carpeta de trabajo (Windows: C:\Proyectos, Linux/Mac: ~/projects)
     4) Abre la terminal y entra a la carpeta del proyecto descomprimido

   - Alternativa B (instalar Git y clonar)
     - Windows: instala "Git for Windows" y luego ejecuta:
       ```bash
       cd "C:\Proyectos"
       git clone https://github.com/Tornadusk/NUAM.git
       cd django-retos-logicos
       ```
     - macOS: instala Command Line Tools (xcode-select --install) o Homebrew; con Git disponible:
       ```bash
       cd ~/projects
       git clone https://github.com/Tornadusk/NUAM.git
       cd django-retos-logicos
       ```
     - Linux (Debian/Ubuntu):
       ```bash
       sudo apt update && sudo apt install -y git
       cd ~/projects
       git clone https://github.com/Tornadusk/NUAM.git
       cd django-retos-logicos
       ```

2. **Crear entorno virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```


   Alternativa rápida (mínima) si solo quieres poner a andar el servidor:
   ```bash
   # Windows
   pip install django 
   # Linux/Mac
   pip3 install django 
   ```


4. **Configurar base de datos**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```


7. **Ejecutar servidor**
   ```bash
   python manage.py runserver
   ```

