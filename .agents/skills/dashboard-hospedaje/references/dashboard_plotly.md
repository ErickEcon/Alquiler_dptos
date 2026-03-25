# Dashboard Plotly — Referencia

## src/dashboard.py

```python
# dashboard.py
# Genera un dashboard HTML interactivo con Plotly.
# El archivo resultante funciona sin servidor: doble clic → abre en navegador.

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import config
from src.metrics import MetricasNegocio


# Paleta de colores consistente en todo el dashboard
PALETA = px.colors.qualitative.Set2
COLOR_PRIMARIO  = "#2E4057"
COLOR_ACENTO    = "#048A81"
COLOR_ALERTA    = "#E07A5F"
COLOR_FONDO     = "#F8F9FA"


def generar_dashboard(
    df: pd.DataFrame,
    metricas: MetricasNegocio,
    ruta_salida: Path,
) -> None:
    """
    Construye el dashboard completo y lo exporta como un único archivo HTML autocontenido.
    Secciones incluidas:
      1. KPI cards (ingreso total, ticket promedio, tasa ocupación, habitación top)
      2. Ingresos mensuales del negocio (línea temporal)
      3. Ingresos anuales por habitación (barras agrupadas)
      4. Ingresos mensuales por habitación (heatmap)
      5. Tasa de ocupación mensual (área)
      6. Ocupación por habitación (barras horizontales)
    """
    figuras = []

    figuras.append(_kpi_cards(metricas))
    figuras.append(_ingresos_mensuales(metricas))
    figuras.append(_ingresos_anuales_por_hab(metricas))
    figuras.append(_heatmap_ingresos(metricas))
    figuras.append(_ocupacion_mensual(metricas))
    figuras.append(_ocupacion_por_habitacion(metricas))

    # Combinar todas las figuras en un HTML único
    html_partes = [_html_header(metricas)]
    for fig in figuras:
        html_partes.append(
            fig.to_html(full_html=False, include_plotlyjs=False)
        )
    html_partes.append("</div></body></html>")

    ruta_salida.write_text("\n".join(html_partes), encoding="utf-8")


# --- Secciones del dashboard ---

def _kpi_cards(m: MetricasNegocio) -> go.Figure:
    """Tarjetas de indicadores clave en la parte superior del dashboard."""
    año_actual = max(m.años_disponibles) if m.años_disponibles else "N/A"
    ingreso_año_actual = m.ingreso_por_año.get(año_actual, 0)

    ultimo_mes = max(m.ingreso_por_mes.keys()) if m.ingreso_por_mes else "N/A"
    ingreso_ultimo_mes = m.ingreso_por_mes.get(ultimo_mes, 0)

    tasa_ocupacion_actual = (
        list(m.tasa_ocupacion_anual.values())[-1]
        if m.tasa_ocupacion_anual else 0
    )

    fig = go.Figure()
    kpis = [
        ("💰 Ingreso Total",      f"S/ {m.ingreso_total:,.0f}",        "Histórico"),
        (f"📅 Ingreso {año_actual}", f"S/ {ingreso_año_actual:,.0f}",   f"Año {año_actual}"),
        (f"🗓 Ingreso {ultimo_mes}", f"S/ {ingreso_ultimo_mes:,.0f}",   "Último mes"),
        ("📊 Ocupación Anual",    f"{tasa_ocupacion_actual}%",          f"Año {año_actual}"),
        ("🏆 Hab. más rentable",  m.habitacion_mas_rentable,            "Por ingresos totales"),
        ("🎫 Ticket Promedio",    f"S/ {m.ticket_promedio:,.0f}",       "Por registro"),
    ]

    for i, (titulo, valor, subtitulo) in enumerate(kpis):
        fig.add_trace(go.Indicator(
            mode="number",
            value=None,  # Usamos title para mostrar texto libre
            title={"text": f"<b>{titulo}</b><br><span style='font-size:1.5em;color:{COLOR_ACENTO}'>{valor}</span><br><span style='font-size:0.8em;color:gray'>{subtitulo}</span>"},
            domain={"row": 0, "column": i},
        ))

    fig.update_layout(
        grid={"rows": 1, "columns": len(kpis)},
        height=180,
        paper_bgcolor=COLOR_FONDO,
        margin=dict(t=20, b=10, l=10, r=10),
    )
    return fig


def _ingresos_mensuales(m: MetricasNegocio) -> go.Figure:
    """Línea temporal de ingresos mensuales del negocio completo."""
    periodos = list(m.ingreso_por_mes.keys())
    ingresos = list(m.ingreso_por_mes.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=periodos,
        y=ingresos,
        mode="lines+markers",
        line=dict(color=COLOR_PRIMARIO, width=2.5),
        marker=dict(size=7, color=COLOR_ACENTO),
        fill="tozeroy",
        fillcolor=f"rgba(4, 138, 129, 0.15)",
        hovertemplate="<b>%{x}</b><br>S/ %{y:,.0f}<extra></extra>",
        name="Ingresos",
    ))

    fig.update_layout(
        title=dict(text="📈 Ingresos Mensuales — Negocio Completo", font_size=16),
        xaxis_title="Mes",
        yaxis_title="Ingresos (S/)",
        height=380,
        paper_bgcolor=COLOR_FONDO,
        plot_bgcolor="white",
        hovermode="x unified",
    )
    return fig


def _ingresos_anuales_por_hab(m: MetricasNegocio) -> go.Figure:
    """Barras agrupadas: ingreso anual por habitación, un grupo por año."""
    df_pivot = m.ingreso_anual_por_hab
    if df_pivot.empty:
        return go.Figure()

    fig = go.Figure()
    for i, año in enumerate(df_pivot.columns):
        fig.add_trace(go.Bar(
            name=str(año),
            x=df_pivot.index.tolist(),
            y=df_pivot[año].tolist(),
            marker_color=PALETA[i % len(PALETA)],
            hovertemplate=f"<b>%{{x}}</b> — {año}<br>S/ %{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="🏠 Ingreso Anual por Habitación", font_size=16),
        barmode="group",
        xaxis_title="Habitación",
        yaxis_title="Ingresos (S/)",
        height=400,
        paper_bgcolor=COLOR_FONDO,
        plot_bgcolor="white",
        legend_title="Año",
    )
    return fig


def _heatmap_ingresos(m: MetricasNegocio) -> go.Figure:
    """Heatmap de ingresos: habitaciones × meses. Permite ver patrones de un vistazo."""
    df_pivot = m.ingreso_mensual_por_hab
    if df_pivot.empty:
        return go.Figure()

    fig = go.Figure(go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns.tolist(),
        y=df_pivot.index.tolist(),
        colorscale="Blues",
        hovertemplate="<b>%{y}</b> — %{x}<br>S/ %{z:,.0f}<extra></extra>",
        colorbar=dict(title="S/"),
    ))

    fig.update_layout(
        title=dict(text="🗓 Heatmap de Ingresos Mensuales por Habitación", font_size=16),
        xaxis_title="Mes",
        yaxis_title="Habitación",
        height=max(300, len(df_pivot.index) * 40 + 100),
        paper_bgcolor=COLOR_FONDO,
    )
    return fig


def _ocupacion_mensual(m: MetricasNegocio) -> go.Figure:
    """Área de tasa de ocupación mensual con línea de referencia al 80%."""
    periodos = list(m.tasa_ocupacion_mensual.keys())
    tasas    = list(m.tasa_ocupacion_mensual.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=periodos, y=tasas,
        mode="lines+markers",
        fill="tozeroy",
        line=dict(color=COLOR_ACENTO, width=2),
        fillcolor=f"rgba(4,138,129,0.2)",
        hovertemplate="<b>%{x}</b><br>Ocupación: %{y}%<extra></extra>",
        name="Ocupación",
    ))
    # Línea de referencia al 80% (objetivo típico de hospedajes)
    fig.add_hline(y=80, line_dash="dash", line_color=COLOR_ALERTA,
                  annotation_text="Meta 80%", annotation_position="right")

    fig.update_layout(
        title=dict(text="📊 Tasa de Ocupación Mensual", font_size=16),
        yaxis=dict(title="Ocupación (%)", range=[0, 105]),
        xaxis_title="Mes",
        height=380,
        paper_bgcolor=COLOR_FONDO,
        plot_bgcolor="white",
    )
    return fig


def _ocupacion_por_habitacion(m: MetricasNegocio) -> go.Figure:
    """Barras horizontales de meses ocupados por habitación."""
    df = m.ocupacion_por_hab
    if df.empty:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=df["tasa_ocupacion_%"],
        y=df[config.COL_HABITACION],
        orientation="h",
        marker_color=COLOR_PRIMARIO,
        text=df["tasa_ocupacion_%"].apply(lambda x: f"{x}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x}% ocupación<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="🏠 Tasa de Ocupación por Habitación (histórico)", font_size=16),
        xaxis=dict(title="Ocupación (%)", range=[0, 115]),
        yaxis_title="Habitación",
        height=max(300, len(df) * 45 + 100),
        paper_bgcolor=COLOR_FONDO,
        plot_bgcolor="white",
    )
    return fig


# --- HTML wrapper ---

def _html_header(m: MetricasNegocio) -> str:
    """Genera el encabezado HTML con CDN de Plotly y estilos del dashboard."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard — {config.NOMBRE_NEGOCIO}</title>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; background: {COLOR_FONDO}; margin: 0; padding: 20px; }}
    h1   {{ color: {COLOR_PRIMARIO}; border-bottom: 3px solid {COLOR_ACENTO}; padding-bottom: 10px; }}
    .subtitulo {{ color: #666; font-size: 0.95em; margin-top: -10px; margin-bottom: 20px; }}
    .contenedor {{ max-width: 1400px; margin: 0 auto; }}
    .grafica {{ background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin-bottom: 24px; padding: 12px; }}
  </style>
</head>
<body>
<div class="contenedor">
  <h1>🏨 {config.NOMBRE_NEGOCIO}</h1>
  <p class="subtitulo">Dashboard de métricas — {m.total_registros} registros · {len(m.habitaciones_unicas)} habitaciones</p>
"""
```
