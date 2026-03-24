# Tareas Programadas — Referencia

## Scheduler simple con `schedule`

```python
# scheduler.py
# Ejecuta tareas automáticamente a horas/días definidos.
# Ideal para reportes diarios, backups o alertas recurrentes.
# Ejecutar con: python scheduler.py (déjalo corriendo en background)

import time
import logging
from pathlib import Path
from datetime import datetime

import schedule

# Configurar logging para tener trazabilidad de las tareas
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),  # Guardar en archivo
        logging.StreamHandler(),               # También mostrar en consola
    ],
)
logger = logging.getLogger(__name__)


# --- Funciones de tareas ---

def generar_reporte_diario() -> None:
    """
    Tarea que se ejecuta todos los días a las 8:00 AM.
    Genera el reporte del día anterior y lo guarda en output/.
    """
    logger.info("▶️  Iniciando generación de reporte diario...")
    try:
        # Aquí va la lógica real del reporte
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        ruta_salida = Path(f"data/output/reporte_{fecha_hoy}.xlsx")
        # ... lógica de generación ...
        logger.info(f"✅ Reporte guardado en {ruta_salida}")
    except Exception as e:
        # Capturar cualquier error para que el scheduler no se detenga
        logger.error(f"❌ Error en reporte diario: {e}")


def verificar_stock_critico() -> None:
    """Tarea que revisa stock cada hora y alerta si hay quiebres."""
    logger.info("🔍 Verificando niveles de stock...")
    # ... lógica de verificación ...


def backup_excel() -> None:
    """Copia los Excel de trabajo a una carpeta de respaldo."""
    logger.info("💾 Realizando backup...")
    # ... lógica de backup ...


# --- Programar las tareas ---

# Reporte: todos los días laborables a las 8:00 AM
schedule.every().monday.at("08:00").do(generar_reporte_diario)
schedule.every().tuesday.at("08:00").do(generar_reporte_diario)
schedule.every().wednesday.at("08:00").do(generar_reporte_diario)
schedule.every().thursday.at("08:00").do(generar_reporte_diario)
schedule.every().friday.at("08:00").do(generar_reporte_diario)

# Stock: cada hora durante horario comercial
schedule.every().hour.do(verificar_stock_critico)

# Backup: cada día a las 6 PM
schedule.every().day.at("18:00").do(backup_excel)


if __name__ == "__main__":
    logger.info("🚀 Scheduler iniciado. Presiona Ctrl+C para detener.")
    logger.info(f"📋 Próximas tareas: {[str(j) for j in schedule.jobs]}")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar tareas pendientes cada minuto
```

---

# Envío de Correos — Referencia

## Enviar reporte por correo con adjunto

```python
# notifier.py
# Envía correos con reportes adjuntos usando solo la stdlib de Python.
# Configurar credenciales en .env (nunca en el código).

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # Cargar variables desde archivo .env


@dataclass
class ConfigCorreo:
    """Agrupa la configuración del servidor SMTP para fácil reutilización."""
    servidor: str = "smtp.gmail.com"
    puerto: int = 587
    usuario: str = os.getenv("EMAIL_USUARIO", "")
    contrasena: str = os.getenv("EMAIL_CONTRASENA", "")  # Usar App Password de Gmail


def enviar_reporte(
    destinatarios: list[str],
    asunto: str,
    cuerpo_html: str,
    adjuntos: list[str] | None = None,
    config: ConfigCorreo | None = None,
) -> None:
    """
    Envía un correo HTML con adjuntos opcionales (Excel, PDF, etc.).

    Args:
        destinatarios: Lista de correos de destino.
        asunto: Línea de asunto del correo.
        cuerpo_html: Contenido del correo en formato HTML.
        adjuntos: Rutas a archivos que se adjuntarán.
        config: Configuración SMTP (usa variables de entorno por defecto).
    """
    if config is None:
        config = ConfigCorreo()

    if not config.usuario or not config.contrasena:
        raise ValueError(
            "Configura EMAIL_USUARIO y EMAIL_CONTRASENA en el archivo .env"
        )

    # Construir el mensaje
    mensaje = MIMEMultipart("mixed")
    mensaje["From"] = config.usuario
    mensaje["To"] = ", ".join(destinatarios)
    mensaje["Subject"] = asunto

    # Agregar cuerpo HTML
    mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    # Adjuntar archivos si se proporcionaron
    for ruta_str in (adjuntos or []):
        ruta = Path(ruta_str)
        if not ruta.exists():
            print(f"  ⚠️  Adjunto no encontrado, se omite: {ruta}")
            continue

        with open(ruta, "rb") as f:
            parte = MIMEBase("application", "octet-stream")
            parte.set_payload(f.read())

        encoders.encode_base64(parte)
        parte.add_header(
            "Content-Disposition",
            f'attachment; filename="{ruta.name}"',
        )
        mensaje.attach(parte)

    # Enviar usando TLS (más seguro que SSL puro)
    with smtplib.SMTP(config.servidor, config.puerto) as servidor:
        servidor.ehlo()
        servidor.starttls()
        servidor.login(config.usuario, config.contrasena)
        servidor.sendmail(config.usuario, destinatarios, mensaje.as_string())

    print(f"✅ Correo enviado a: {', '.join(destinatarios)}")


# --- Plantilla HTML de reporte ---

def plantilla_reporte_html(titulo: str, resumen: dict, tabla_datos: str = "") -> str:
    """Genera el HTML del correo con un diseño limpio y profesional."""
    filas_resumen = "".join(
        f"<tr><td><b>{k}</b></td><td>{v}</td></tr>"
        for k, v in resumen.items()
    )
    return f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2E4057;">{titulo}</h2>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
            {filas_resumen}
        </table>
        {f"<br>{tabla_datos}" if tabla_datos else ""}
        <p style="color: #888; font-size: 12px;">
            Generado automáticamente. No responder a este correo.
        </p>
    </body></html>
    """
```
