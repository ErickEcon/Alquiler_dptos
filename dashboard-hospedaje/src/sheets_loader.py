# sheets_loader.py
import gspread
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from pathlib import Path

import config

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
        Columna fecha_registro ignorada.
    """
    if not config.SPREADSHEET_ID:
        raise ValueError(
            "SPREADSHEET_ID está vacío. Agrégalo al archivo .env\n"
        )

    print(f"🔗 Conectando a Google Sheets (ID: {config.SPREADSHEET_ID[:20]}...)...")
    cliente = _autenticar()

    try:
        hoja = cliente.open_by_key(config.SPREADSHEET_ID).worksheet(config.SHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        raise gspread.exceptions.SpreadsheetNotFound(
            f"Sheet no encontrado (o no compartido con el service account)."
        )
    except gspread.exceptions.WorksheetNotFound:
        hojas_disponibles = [ws.title for ws in cliente.open_by_key(config.SPREADSHEET_ID).worksheets()]
        raise gspread.exceptions.WorksheetNotFound(
            f"Pestaña '{config.SHEET_NAME}' no encontrada. "
            f"Pestañas disponibles: {hojas_disponibles}"
        )

    registros = hoja.get_all_records(empty2zero=False, head=1)

    if not registros:
        raise ValueError("El Google Sheet está vacío o no tiene datos bajo los encabezados.")

    df = pd.DataFrame(registros)
    return _limpiar_dataframe(df)

def _limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Normalizar nombres de columnas: minúsculas, sin espacios
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace("/", "_")
    )

    columnas_ignoradas = ["fecha_registro", "fecha_de_registro"]
    df = df.drop(columns=[c for c in columnas_ignoradas if c in df.columns], errors="ignore")

    # Mapeo según los headers exactos que envía registro_alquileres (en crudo ya normalizados)
    mapeo_columnas = {
        "habitación_dpto": config.COL_HABITACION,
        "habitacion_dpto": config.COL_HABITACION,
        "nombre_del_inquilino": config.COL_INQUILINO,
        "nombre_inquilino": config.COL_INQUILINO,
        "precio_pagado": config.COL_PRECIO,
        "precio": config.COL_PRECIO,
        "fecha_de_inicio": config.COL_FECHA_INICIO,
        "fecha_inicio": config.COL_FECHA_INICIO,
    }
    df = df.rename(columns={k: v for k, v in mapeo_columnas.items() if k in df.columns})

    columnas_requeridas = [
        config.COL_HABITACION, config.COL_INQUILINO,
        config.COL_PRECIO, config.COL_FECHA_INICIO,
    ]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Columnas requeridas no encontradas: {faltantes}\n"
            f"Columnas disponibles en el sheet: {df.columns.tolist()}"
        )

    df = df.dropna(subset=[config.COL_HABITACION, config.COL_PRECIO])
    df = df[df[config.COL_HABITACION].astype(str).str.strip() != ""]

    df[config.COL_PRECIO] = (
        df[config.COL_PRECIO]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
        .replace("", np.nan)
        .astype(float)
    )

    df[config.COL_FECHA_INICIO] = pd.to_datetime(
        df[config.COL_FECHA_INICIO],
        dayfirst=True,
        errors="coerce",
    )

    fechas_invalidas = df[config.COL_FECHA_INICIO].isna().sum()
    if fechas_invalidas > 0:
        print(f"  ⚠️  {fechas_invalidas} fechas inválidas en '{config.COL_FECHA_INICIO}' (se omitirán).")
        df = df.dropna(subset=[config.COL_FECHA_INICIO])

    df["año"]  = df[config.COL_FECHA_INICIO].dt.year
    df["mes"]  = df[config.COL_FECHA_INICIO].dt.month
    df["periodo"] = df[config.COL_FECHA_INICIO].dt.to_period("M").astype(str)

    return df.reset_index(drop=True)
