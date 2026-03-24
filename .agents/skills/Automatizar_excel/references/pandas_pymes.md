# Pandas para PYMEs — Referencia

## Limpieza de datos típicos de PYMEs

```python
import pandas as pd
import numpy as np
from typing import Optional

def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpieza estándar a un DataFrame que proviene de Excel manual.
    Cubre los problemas más comunes: espacios, duplicados, tipos de datos.
    """
    # Eliminar filas y columnas completamente vacías (frecuente en Excel manuales)
    df = df.dropna(how="all").dropna(axis=1, how="all")

    # Limpiar espacios en columnas de texto
    columnas_texto = df.select_dtypes(include="object").columns
    df[columnas_texto] = df[columnas_texto].apply(
        lambda col: col.str.strip().str.upper()  # Normalizar a mayúsculas
    )

    # Eliminar filas duplicadas
    filas_antes = len(df)
    df = df.drop_duplicates()
    filas_eliminadas = filas_antes - len(df)
    if filas_eliminadas > 0:
        print(f"  ⚠️  Se eliminaron {filas_eliminadas} filas duplicadas.")

    # Resetear índice tras todas las operaciones de filtrado
    return df.reset_index(drop=True)


def convertir_fechas(
    df: pd.DataFrame,
    columnas_fecha: list[str],
    formato: Optional[str] = None,
) -> pd.DataFrame:
    """
    Convierte columnas de texto a datetime con manejo de errores.
    Muy útil cuando el Excel mezcla formatos de fecha (dd/mm/aa, mm-dd-yyyy, etc.)
    """
    for col in columnas_fecha:
        if col not in df.columns:
            print(f"  ⚠️  Columna '{col}' no encontrada, se omite.")
            continue

        # errors="coerce" convierte valores inválidos a NaT en vez de lanzar error
        df[col] = pd.to_datetime(df[col], format=formato, errors="coerce", dayfirst=True)

        invalidos = df[col].isna().sum()
        if invalidos > 0:
            print(f"  ⚠️  {invalidos} fechas inválidas en '{col}' (convertidas a NaT).")

    return df
```

## Análisis de ventas

```python
def resumen_ventas(df: pd.DataFrame, col_fecha: str, col_monto: str, col_producto: str) -> dict:
    """
    Genera un resumen ejecutivo de ventas desde un DataFrame.
    Retorna un dict con métricas clave listas para reportar.
    """
    # Asegurar que la columna de monto sea numérica
    df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)

    resumen = {
        "total_ventas": df[col_monto].sum(),
        "ticket_promedio": df[col_monto].mean(),
        "numero_transacciones": len(df),
        # Top 5 productos por monto total
        "top_productos": (
            df.groupby(col_producto)[col_monto]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .to_dict()
        ),
        # Ventas agrupadas por mes
        "ventas_por_mes": (
            df.groupby(df[col_fecha].dt.to_period("M"))[col_monto]
            .sum()
            .to_dict()
        ),
    }

    return resumen
```

## Alertas de inventario

```python
def detectar_quiebre_stock(
    df: pd.DataFrame,
    col_producto: str,
    col_stock: str,
    umbral_minimo: int = 10,
) -> pd.DataFrame:
    """
    Filtra productos por debajo del umbral mínimo de stock.
    Retorna solo los productos que necesitan reabastecimiento.
    """
    df[col_stock] = pd.to_numeric(df[col_stock], errors="coerce").fillna(0)

    productos_bajos = df[df[col_stock] <= umbral_minimo].copy()
    productos_bajos["urgencia"] = productos_bajos[col_stock].apply(
        lambda x: "🔴 CRÍTICO" if x == 0 else "🟡 BAJO"
    )

    return productos_bajos[[col_producto, col_stock, "urgencia"]].sort_values(col_stock)
```
