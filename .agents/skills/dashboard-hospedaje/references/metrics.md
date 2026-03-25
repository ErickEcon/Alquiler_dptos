# Métricas del Negocio — Referencia

## src/metrics.py

```python
# metrics.py
# Calcula todas las métricas del negocio de alquiler de habitaciones.
# Recibe el DataFrame limpio y retorna un dict estructurado con todos los indicadores.

import pandas as pd
import numpy as np
from dataclasses import dataclass, field

import config


@dataclass
class MetricasNegocio:
    """
    Contenedor tipado de todas las métricas del negocio.
    Usar dataclass evita diccionarios con typos y facilita el autocompletado.
    """
    # --- Ingresos globales ---
    ingreso_total: float = 0.0
    ingreso_por_año: dict[int, float] = field(default_factory=dict)
    ingreso_por_mes: dict[str, float] = field(default_factory=dict)   # "2024-03" → monto

    # --- Ingresos por habitación ---
    ingreso_anual_por_hab: pd.DataFrame = field(default_factory=pd.DataFrame)  # hab × año
    ingreso_mensual_por_hab: pd.DataFrame = field(default_factory=pd.DataFrame)

    # --- Ocupación ---
    tasa_ocupacion_anual: dict[int, float] = field(default_factory=dict)   # año → %
    tasa_ocupacion_mensual: dict[str, float] = field(default_factory=dict) # "2024-03" → %
    ocupacion_por_hab: pd.DataFrame = field(default_factory=pd.DataFrame)  # hab → meses ocupados

    # --- KPIs adicionales ---
    ticket_promedio: float = 0.0
    habitacion_mas_rentable: str = ""
    habitacion_menos_rentable: str = ""
    mes_pico_ingresos: str = ""
    mes_valle_ingresos: str = ""
    habitaciones_unicas: list[str] = field(default_factory=list)
    años_disponibles: list[int] = field(default_factory=list)
    total_registros: int = 0


def calcular_metricas(df: pd.DataFrame) -> MetricasNegocio:
    """
    Punto de entrada principal. Calcula todas las métricas a partir del DataFrame limpio.

    Args:
        df: DataFrame retornado por sheets_loader.cargar_datos_sheets()

    Returns:
        MetricasNegocio con todos los indicadores calculados.
    """
    m = MetricasNegocio()

    col_hab    = config.COL_HABITACION
    col_precio = config.COL_PRECIO

    m.total_registros   = len(df)
    m.habitaciones_unicas = sorted(df[col_hab].unique().tolist())
    m.años_disponibles    = sorted(df["año"].unique().tolist())

    # --- Ingresos globales ---
    m.ingreso_total = float(df[col_precio].sum())
    m.ticket_promedio = float(df[col_precio].mean())

    # Ingreso anual: suma de precios por año
    m.ingreso_por_año = (
        df.groupby("año")[col_precio].sum()
          .round(2)
          .to_dict()
    )

    # Ingreso mensual: suma de precios por periodo "YYYY-MM"
    m.ingreso_por_mes = (
        df.groupby("periodo")[col_precio].sum()
          .sort_index()
          .round(2)
          .to_dict()
    )

    # --- Ingresos por habitación ---
    # Tabla pivote: habitaciones como filas, años como columnas
    m.ingreso_anual_por_hab = (
        df.pivot_table(
            index=col_hab,
            columns="año",
            values=col_precio,
            aggfunc="sum",
            fill_value=0,
        ).round(2)
    )

    # Tabla pivote: habitaciones como filas, periodos mensuales como columnas
    m.ingreso_mensual_por_hab = (
        df.pivot_table(
            index=col_hab,
            columns="periodo",
            values=col_precio,
            aggfunc="sum",
            fill_value=0,
        ).round(2)
    )

    # --- Tasa de ocupación ---
    # Definición: meses con al menos 1 registro / total meses posibles × 100
    m.tasa_ocupacion_anual  = _calcular_ocupacion_anual(df)
    m.tasa_ocupacion_mensual = _calcular_ocupacion_mensual(df)
    m.ocupacion_por_hab     = _calcular_ocupacion_por_habitacion(df)

    # --- KPIs adicionales ---
    ingresos_por_hab_total = df.groupby(col_hab)[col_precio].sum()
    m.habitacion_mas_rentable  = str(ingresos_por_hab_total.idxmax())
    m.habitacion_menos_rentable = str(ingresos_por_hab_total.idxmin())

    if m.ingreso_por_mes:
        m.mes_pico_ingresos  = max(m.ingreso_por_mes, key=m.ingreso_por_mes.get)
        m.mes_valle_ingresos = min(m.ingreso_por_mes, key=m.ingreso_por_mes.get)

    return m


def _calcular_ocupacion_anual(df: pd.DataFrame) -> dict[int, float]:
    """
    Tasa de ocupación anual = habitaciones con ≥1 registro ese año /
    (total_habitaciones × 12 meses) × 100
    """
    resultado = {}
    for año in df["año"].unique():
        df_año = df[df["año"] == año]
        # Contar combinaciones únicas hab-mes (evitar contar doble si hay 2 registros el mismo mes)
        combos_unicos = df_año.groupby([config.COL_HABITACION, "mes"]).ngroups
        capacidad_max = config.TOTAL_HABITACIONES * 12
        resultado[int(año)] = round((combos_unicos / capacidad_max) * 100, 1)
    return dict(sorted(resultado.items()))


def _calcular_ocupacion_mensual(df: pd.DataFrame) -> dict[str, float]:
    """
    Tasa de ocupación mensual = habitaciones con registro ese mes /
    total_habitaciones × 100
    """
    resultado = {}
    for periodo in df["periodo"].unique():
        df_mes = df[df["periodo"] == periodo]
        habs_ocupadas = df_mes[config.COL_HABITACION].nunique()
        resultado[periodo] = round((habs_ocupadas / config.TOTAL_HABITACIONES) * 100, 1)
    return dict(sorted(resultado.items()))


def _calcular_ocupacion_por_habitacion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Por cada habitación: cuántos meses distintos tuvo al menos un registro.
    Retorna DataFrame con columnas: habitacion, meses_ocupados, tasa_ocupacion_%
    """
    meses_por_hab = (
        df.groupby(config.COL_HABITACION)["periodo"]
          .nunique()
          .reset_index()
          .rename(columns={"periodo": "meses_ocupados"})
    )

    # Calcular total de meses posibles (años disponibles × 12)
    total_meses = df["año"].nunique() * 12
    meses_por_hab["tasa_ocupacion_%"] = (
        (meses_por_hab["meses_ocupados"] / total_meses * 100).round(1)
    )

    return meses_por_hab.sort_values("meses_ocupados", ascending=False)
```
