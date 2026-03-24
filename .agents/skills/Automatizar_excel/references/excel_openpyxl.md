# Excel con openpyxl — Referencia para PYMEs

## Lectura básica de Excel

```python
import openpyxl
from pathlib import Path
from typing import Generator

def leer_hoja(ruta_archivo: str, nombre_hoja: str = "Sheet1") -> list[dict]:
    """
    Lee una hoja de Excel y retorna una lista de diccionarios.
    Cada fila se convierte en un dict con los encabezados como claves.
    """
    ruta = Path(ruta_archivo)

    # Validar que el archivo exista antes de intentar abrirlo
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    # read_only=True mejora el rendimiento para archivos grandes
    workbook = openpyxl.load_workbook(ruta, read_only=True, data_only=True)

    if nombre_hoja not in workbook.sheetnames:
        raise ValueError(
            f"La hoja '{nombre_hoja}' no existe. "
            f"Hojas disponibles: {workbook.sheetnames}"
        )

    hoja = workbook[nombre_hoja]
    filas = hoja.iter_rows(values_only=True)

    # La primera fila se usa como encabezados del diccionario
    encabezados = [str(celda) for celda in next(filas)]

    # Convertir cada fila en un dict ignorando filas completamente vacías
    registros = [
        dict(zip(encabezados, fila))
        for fila in filas
        if any(celda is not None for celda in fila)
    ]

    workbook.close()
    return registros
```

## Escritura con formato

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def crear_reporte_excel(datos: list[dict], ruta_salida: str) -> None:
    """
    Crea un reporte Excel con encabezados formateados y autoajuste de columnas.
    Ideal para reportes que serán revisados por humanos.
    """
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Reporte"

    if not datos:
        workbook.save(ruta_salida)
        return

    # --- Estilos reutilizables ---
    estilo_encabezado = Font(bold=True, color="FFFFFF")
    fondo_encabezado = PatternFill(fill_type="solid", fgColor="2E4057")
    alineacion_centro = Alignment(horizontal="center", vertical="center")

    borde_delgado = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # --- Encabezados ---
    encabezados = list(datos[0].keys())
    for col_idx, nombre in enumerate(encabezados, start=1):
        celda = hoja.cell(row=1, column=col_idx, value=nombre)
        celda.font = estilo_encabezado
        celda.fill = fondo_encabezado
        celda.alignment = alineacion_centro
        celda.border = borde_delgado

    # --- Datos ---
    for fila_idx, registro in enumerate(datos, start=2):
        for col_idx, valor in enumerate(registro.values(), start=1):
            celda = hoja.cell(row=fila_idx, column=col_idx, value=valor)
            celda.border = borde_delgado
            # Alternar color de fila para mejor lectura
            if fila_idx % 2 == 0:
                celda.fill = PatternFill(fill_type="solid", fgColor="F0F4F8")

    # --- Autoajuste de columnas ---
    for col_idx, nombre in enumerate(encabezados, start=1):
        letra_col = get_column_letter(col_idx)
        ancho_max = max(
            len(str(nombre)),
            *(len(str(registro.get(nombre, ""))) for registro in datos),
        )
        # Limitar ancho máximo para evitar columnas gigantes
        hoja.column_dimensions[letra_col].width = min(ancho_max + 4, 50)

    workbook.save(ruta_salida)
    print(f"✅ Reporte guardado en: {ruta_salida}")
```

## Lectura de múltiples archivos (consolidación)

```python
from pathlib import Path
import pandas as pd

def consolidar_excel(carpeta: str, patron: str = "*.xlsx") -> pd.DataFrame:
    """
    Une todos los archivos Excel de una carpeta en un único DataFrame.
    Agrega una columna 'archivo_origen' para trazabilidad.
    """
    archivos = list(Path(carpeta).glob(patron))

    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron archivos con patrón '{patron}' en '{carpeta}'"
        )

    # Leer cada archivo y etiquetar su origen
    dfs = []
    for archivo in archivos:
        try:
            df = pd.read_excel(archivo)
            df["archivo_origen"] = archivo.name  # Columna de trazabilidad
            dfs.append(df)
            print(f"  ✅ Leído: {archivo.name} ({len(df)} filas)")
        except Exception as e:
            # No detener el proceso si un archivo falla; solo advertir
            print(f"  ⚠️  Error en {archivo.name}: {e}")

    if not dfs:
        raise ValueError("Ningún archivo pudo leerse correctamente.")

    return pd.concat(dfs, ignore_index=True)
```
