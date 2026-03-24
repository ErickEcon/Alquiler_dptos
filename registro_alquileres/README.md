# Sistema de Registro de Alquileres (Cloud & Google Sheets)

Sistema automatizado para registrar el ingreso de nuevos inquilinos a departamentos y habitaciones, desarrollado con FastAPI y Python. Los datos son almacenados de forma segura en **Google Sheets**, lo que permite alojar la aplicación en plataformas en la nube gratuitas (como Render, Koyeb, Railway) sin perder tu información cuando el servidor se reinicia.

## Requisitos Previos
- Python 3.8 o superior
- Un archivo `credentials.json` generado desde Google Cloud Console (Service Account) con las APIs de Google Sheets y Google Drive habilitadas.

## Configuración Principal
1. Asegúrate de colocar tu archivo `credentials.json` en la raíz de este proyecto (`d:\Python\Automatizacion_Excel\registro_alquileres\`).
2. Crea una hoja de cálculo nueva en Google Drive y nómbrala exactamente **"Alquileres Dptos"**.
3. Abre tu archivo `credentials.json` con un bloc de notas, copia el correo electrónico que dice `client_email` (termina en `@...iam.gserviceaccount.com`).
4. Ve a tu hoja de Google Sheets, haz clic en el botón verde de "Compartir" y dale permisos de **Editor** a ese correo.
5. Instala las dependencias necesarias:
   ```cmd
   pip install -r requirements.txt
   ```

## Ejecución Local de Prueba
Inicia el servidor local de FastAPI con el siguiente comando (puedes detenerlo con `Ctrl+C`):
```cmd
python -m uvicorn main:app --port 8000 --reload
```

## Despliegue en la Nube (Ejemplo: Render.com)
1. Sube tu proyecto a GitHub (importante: ignorar el `credentials.json` en `.gitignore` para no filtrar tus claves).
2. Conecta el repositorio a Render (Web Service).
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5. **Secret Files:** En la configuración de Render, ve al apartado de Secret Files, crea un archivo llamado `credentials.json` y pega ahí el contenido de tu archivo clave original. ¡Listo!
