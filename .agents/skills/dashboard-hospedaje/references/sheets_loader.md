# Google Sheets Loader — Referencia

## Configuración inicial de credenciales

Para usar la API de Google Sheets necesitas un **Service Account**:
1. Ve a [console.cloud.google.com](https://console.cloud.google.com)
2. Crea un proyecto → Habilita "Google Sheets API" y "Google Drive API"
3. Crea una cuenta de servicio → descarga el JSON como `credentials.json`
4. Comparte el Google Sheet con el email de la cuenta de servicio (`...@....iam.gserviceaccount.com`)

---

## src/sheets_loader.py

```python
# sheets_loader.py
# Descarga los datos del Google Sheet y los devuelve como DataFrame limpio.
# Usa gspread con autenticación por service account (no requiere OAuth del usuario).

import gspread
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from pathlib import Path

import config


# Scopes mínimos necesarios para leer Google Sheets (principio de mínimo privilegio)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _autenticar() -> gspread.Client:
    """
    Autenticar con Google API usando el archivo credentials.json del service account.
    Retorna un cliente gspread listo para usar.
    """
    if not config.CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró credentials.json en: {config.CREDENTIALS_PATH}\n"
            "Descárgalo desde Google Cloud Console y colócalo en la raíz del proyecto."
        )

    credenciales = Credentials.from_service_account_file(
        str(config.CREDENTIALS_PATH),
        scopes=SCOPES,
    )
    return gspread.authorize(credenciales)


def cargar_datos_sheets() -> pd.DataFrame:
    """
    Descarga todos los registros del Google Sheet configurado y los limpia.

    Returns:
        DataFrame con columnas: habitacion, inquilino, precio_pagado, fecha_inicio
        Columna fecha_registro ignorada (no aporta valor al análisis).

    Raises:
        FileNotFoundError: Si credentials.json no existe.
        gspread.exceptions.SpreadsheetNotFound: Si el SPREADSHEET_ID es inválido
            o el sheet no fue compartido con el service account.
    """
    if not config.SPREADSHEET_ID:
        raise ValueError(
            "SPREADSHEET_ID está vacío. Agrégalo al archivo .env\n"
            "Puedes encontrarlo en la URL del sheet: "
            "docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit"
        )

    print(f"🔗 Conectando a Google Sheets (ID: {config.SPREADSHEET_ID[:20]}...)...")
    cliente = _autenticar()

    try:
        hoja = cliente.open_by_key(config.SPREADSHEET_ID).worksheet(config.SHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        raise gspread.exceptions.SpreadsheetNotFound(
            f"Sheet no encontrado. Verifica que:\n"
            f"  1. SPREADSHEET_ID sea correcto en .env\n"
            f"  2. El sheet fue compartido con la cuenta de servicio en credentials.json"
        )
    except gspread.exceptions.WorksheetNotFound:
        hojas_disponibles = [ws.title for ws in cliente.open_by_key(config.SPREADSHEET_ID).worksheets()]
        raise gspread.exceptions.WorksheetNotFound(
            f"Pestaña '{config.SHEET_NAME}' no encontrada. "
            f"Pestañas disponibles: {hojas_disponibles}"
        )

    # get_all_records() convierte automáticamente la primera fila en encabezados
    registros = hoja.get_all_records(empty2zero=False, head=1)

    if not registros:
        raise ValueError("El Google Sheet está vacío o no tiene datos bajo los encabezados.")

    df = pd.DataFrame(registros)
    return _limpiar_dataframe(df)


def _limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza y limpia el DataFrame crudo del Google Sheet.
    - Estandariza nombres de columnas
    - Convierte tipos de datos
    - Elimina filas vacías o inválidas
    """
    # Normalizar nombres de columnas: minúsculas, sin espacios
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace("/", "_")
    )

    # Eliminar columna fecha_registro si existe (no aporta al análisis)
    columnas_ignoradas = ["fecha_registro", "fecha_de_registro"]
    df = df.drop(columns=[c for c in columnas_ignoradas if c in df.columns], errors="ignore")

    # Renombrar columnas al estándar esperado por metrics.py
    mapeo_columnas = {
        "habitacion_dpto": config.COL_HABITACION,
        "habitación": config.COL_HABITACION,
        "dpto": config.COL_HABITACION,
        "nombre_del_inquilino": config.COL_INQUILINO,
        "nombre_inquilino": config.COL_INQUILINO,
        "precio": config.COL_PRECIO,
        "monto": config.COL_PRECIO,
        "fecha_de_inicio": config.COL_FECHA_INICIO,
    }
    df = df.rename(columns={k: v for k, v in mapeo_columnas.items() if k in df.columns})

    # Verificar que las columnas requeridas existan tras el renombrado
    columnas_requeridas = [
        config.COL_HABITACION, config.COL_INQUILINO,
        config.COL_PRECIO, config.COL_FECHA_INICIO,
    ]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Columnas requeridas no encontradas: {faltantes}\n"
            f"Columnas disponibles en el sheet: {df.columns.tolist()}\n"
            f"Ajusta el mapeo en config.py si tus columnas tienen nombres distintos."
        )

    # Eliminar filas donde habitación o precio estén vacíos
    df = df.dropna(subset=[config.COL_HABITACION, config.COL_PRECIO])
    df = df[df[config.COL_HABITACION].astype(str).str.strip() != ""]

    # Convertir precio a numérico (puede venir como string con "S/" o comas)
    df[config.COL_PRECIO] = (
        df[config.COL_PRECIO]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)   # Quitar símbolos de moneda
        .replace("", np.nan)
        .astype(float)
    )

    # Convertir fecha_inicio a datetime con soporte para múltiples formatos
    df[config.COL_FECHA_INICIO] = pd.to_datetime(
        df[config.COL_FECHA_INICIO],
        dayfirst=True,
        errors="coerce",
    )

    # Advertir sobre fechas inválidas pero no detener el proceso
    fechas_invalidas = df[config.COL_FECHA_INICIO].isna().sum()
    if fechas_invalidas > 0:
        print(f"  ⚠️  {fechas_invalidas} fechas inválidas en '{config.COL_FECHA_INICIO}' (se omitirán).")
        df = df.dropna(subset=[config.COL_FECHA_INICIO])

    # Agregar columnas auxiliares para facilitar agrupaciones en metrics.py
    df["año"]  = df[config.COL_FECHA_INICIO].dt.year
    df["mes"]  = df[config.COL_FECHA_INICIO].dt.month
    df["periodo"] = df[config.COL_FECHA_INICIO].dt.to_period("M").astype(str)  # "2024-03"

    return df.reset_index(drop=True)
```
