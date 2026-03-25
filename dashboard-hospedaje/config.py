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
TOTAL_HABITACIONES = int(os.getenv("TOTAL_HABITACIONES", "13")) # 13 defined in the registration project
NOMBRE_NEGOCIO     = os.getenv("NOMBRE_NEGOCIO", "Alquileres Dptos Dashboard")
