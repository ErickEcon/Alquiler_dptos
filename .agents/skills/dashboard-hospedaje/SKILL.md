---
name: dashboard-hospedaje
description: >
  Skill para generar un dashboard interactivo con Plotly y un informe PDF con ReportLab
  a partir de datos de alquiler de habitaciones/departamentos descargados desde Google Sheets
  via API. Úsala cuando el usuario quiera visualizar métricas de su negocio de hospedaje,
  generar reportes de ingresos por habitación, tasa de ocupación, estadísticas mensuales o
  anuales, o exportar un informe PDF del negocio. También actívala cuando mencione palabras
  como "dashboard", "reporte de ingresos", "ocupación", "métricas del negocio", "informe PDF",
  "Google Sheets hospedaje", o cualquier combinación de análisis + alquiler de habitaciones.
---

# Dashboard de Hospedaje — Google Sheets → Plotly + ReportLab

Genera un dashboard interactivo HTML y un informe PDF desde datos de alquiler mensual
almacenados en Google Sheets. Estructura de datos esperada:

| fecha_registro | habitacion | inquilino | precio_pagado | fecha_inicio |
|----------------|------------|-----------|---------------|--------------|
| 2024-03-01     | "Hab 101"  | "Juan P." | 850.00        | 2024-03-01   |

---

## 🗂 Estructura del proyecto

```
dashboard-hospedaje/
├── config.py              # Rutas, IDs, parámetros configurables
├── main.py                # Punto de entrada: descarga → procesa → genera salidas
├── requirements.txt
├── .env                   # Credenciales (NUNCA subir a git)
├── credentials.json       # Service account de Google API
├── src/
│   ├── __init__.py
│   ├── sheets_loader.py   # Descarga y limpieza desde Google Sheets
│   ├── metrics.py         # Cálculo de todas las métricas
│   ├── dashboard.py       # Dashboard interactivo con Plotly
│   └── pdf_report.py      # Informe PDF con ReportLab
└── output/
    ├── dashboard.html
    └── informe_hospedaje.pdf
```

---

## 📚 Referencias por módulo

Lee el archivo correspondiente **antes** de generar código para ese módulo:

- **Conexión Google Sheets API** → `references/sheets_loader.md`
- **Cálculo de métricas** → `references/metrics.md`
- **Dashboard Plotly** → `references/dashboard_plotly.md`
- **Informe PDF ReportLab** → `references/pdf_reportlab.md`

---

## ⚙️ config.py y .env

```python
# config.py — Centraliza toda la configuración del proyecto
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Rutas ---
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

CREDENTIALS_PATH = BASE_DIR / "credentials.json"

# --- Google Sheets ---
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")   # ID del sheet en la URL
SHEET_NAME     = os.getenv("SHEET_NAME", "Hoja 1")  # Nombre de la pestaña

# --- Columnas (adaptar si el usuario tiene nombres distintos) ---
COL_HABITACION   = "habitacion"
COL_INQUILINO    = "inquilino"
COL_PRECIO       = "precio_pagado"
COL_FECHA_INICIO = "fecha_inicio"

# --- Negocio ---
TOTAL_HABITACIONES = int(os.getenv("TOTAL_HABITACIONES", "10"))
NOMBRE_NEGOCIO     = os.getenv("NOMBRE_NEGOCIO", "Mi Hospedaje")
```

```ini
# .env
SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms
SHEET_NAME=Registros
TOTAL_HABITACIONES=10
NOMBRE_NEGOCIO=Hospedaje Los Pinos
```

---

## 🚀 main.py

```python
# main.py — Orquesta todo el flujo de extremo a extremo
from src.sheets_loader import cargar_datos_sheets
from src.metrics import calcular_metricas
from src.dashboard import generar_dashboard
from src.pdf_report import generar_pdf
from config import OUTPUT_DIR
import config

def main() -> None:
    print(f"🏨 {config.NOMBRE_NEGOCIO} — Generando dashboard e informe...\n")

    # 1. Descargar y limpiar datos desde Google Sheets
    df = cargar_datos_sheets()
    print(f"✅ {len(df)} registros cargados.\n")

    # 2. Calcular todas las métricas del negocio
    metricas = calcular_metricas(df)

    # 3. Generar dashboard HTML interactivo con Plotly
    ruta_html = OUTPUT_DIR / "dashboard.html"
    generar_dashboard(df, metricas, ruta_html)
    print(f"📊 Dashboard guardado en: {ruta_html}")

    # 4. Generar informe PDF con ReportLab
    ruta_pdf = OUTPUT_DIR / "informe_hospedaje.pdf"
    generar_pdf(df, metricas, ruta_pdf)
    print(f"📄 Informe PDF guardado en: {ruta_pdf}")

    print("\n🎉 ¡Listo! Abre dashboard.html en tu navegador.")


if __name__ == "__main__":
    main()
```

---

## 📦 requirements.txt

```
gspread==6.1.2
google-auth==2.29.0
pandas==2.2.2
plotly==5.22.0
reportlab==4.2.0
python-dotenv==1.0.1
numpy==1.26.4
```

---

## ✅ Checklist antes de entregar código

- [ ] `credentials.json` referenciado desde `.env`, nunca hardcodeado
- [ ] Columnas leídas desde `config.py`, no strings literales dispersos
- [ ] Todas las funciones tienen `type hints` y docstring
- [ ] Errores de API / archivo faltante manejados con mensajes claros
- [ ] El dashboard funciona abriéndolo directo en el navegador (sin servidor)
- [ ] El PDF incluye: portada, métricas clave, tabla por habitación y gráficas
