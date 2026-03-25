# pdf_report.py
from pathlib import Path
from datetime import datetime
import io

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable,
)
from reportlab.platypus.flowables import KeepTogether

import config
from src.metrics import MetricasNegocio

COLOR_PRIMARIO  = colors.HexColor("#2E4057")
COLOR_ACENTO    = colors.HexColor("#048A81")
COLOR_CLARO     = colors.HexColor("#E8F4F3")
COLOR_ALERTA    = colors.HexColor("#E07A5F")
COLOR_GRIS      = colors.HexColor("#F0F0F0")

def generar_pdf(
    df: pd.DataFrame,
    metricas: MetricasNegocio,
    ruta_salida: Path,
) -> None:
    doc = SimpleDocTemplate(
        str(ruta_salida),
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    estilos = _crear_estilos()
    elementos = []

    elementos += _seccion_portada(estilos, metricas)
    elementos.append(PageBreak())

    elementos += _seccion_kpis(estilos, metricas)
    elementos.append(Spacer(1, 0.8 * cm))

    elementos += _seccion_ingresos_por_hab(estilos, metricas)
    elementos.append(Spacer(1, 0.8 * cm))

    elementos += _seccion_ocupacion(estilos, metricas)
    elementos.append(Spacer(1, 0.8 * cm))

    elementos += _seccion_graficas(estilos, metricas)

    doc.build(
        elementos,
        onFirstPage=_pie_pagina,
        onLaterPages=_pie_pagina,
    )

def _seccion_portada(estilos: dict, m: MetricasNegocio) -> list:
    año_actual = max(m.años_disponibles) if m.años_disponibles else "N/A"
    return [
        Spacer(1, 3 * cm),
        Paragraph(config.NOMBRE_NEGOCIO, estilos["titulo_portada"]),
        Spacer(1, 0.5 * cm),
        Paragraph("Informe de Gestión — Métricas y Estadísticas", estilos["subtitulo_portada"]),
        Spacer(1, 0.5 * cm),
        HRFlowable(width="100%", thickness=3, color=COLOR_ACENTO),
        Spacer(1, 1.5 * cm),
        Paragraph(f"Período analizado: {min(m.años_disponibles) if m.años_disponibles else '-'} – {max(m.años_disponibles) if m.años_disponibles else '-'}", estilos["normal"]),
        Paragraph(f"Habitaciones registradas: {len(m.habitaciones_unicas)}", estilos["normal"]),
        Paragraph(f"Total de registros: {m.total_registros}", estilos["normal"]),
        Spacer(1, 1 * cm),
        Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", estilos["pie"]),
    ]

def _seccion_kpis(estilos: dict, m: MetricasNegocio) -> list:
    año_actual = max(m.años_disponibles) if m.años_disponibles else "N/A"
    ultimo_mes = max(m.ingreso_por_mes.keys()) if m.ingreso_por_mes else "N/A"
    tasa_actual = list(m.tasa_ocupacion_anual.values())[-1] if m.tasa_ocupacion_anual else 0

    kpis = [
        ["Indicador", "Valor", "Referencia"],
        ["💰 Ingreso histórico total", f"S/ {m.ingreso_total:,.2f}", "Todos los años"],
        [f"📅 Ingreso año {año_actual}", f"S/ {m.ingreso_por_año.get(año_actual, 0):,.2f}", str(año_actual)],
        [f"🗓 Ingreso {ultimo_mes}", f"S/ {m.ingreso_por_mes.get(ultimo_mes, 0):,.2f}", "Último mes"],
        ["📊 Tasa de ocupación anual", f"{tasa_actual}%", f"Año {año_actual}"],
        ["🎫 Ticket promedio", f"S/ {m.ticket_promedio:,.2f}", "Por registro"],
        ["🏆 Habitación más rentable", m.habitacion_mas_rentable, "Por ingresos totales"],
        ["📈 Mes de mayor ingreso", m.mes_pico_ingresos, "Histórico"],
        ["📉 Mes de menor ingreso", m.mes_valle_ingresos, "Histórico"],
    ]

    return [
        Paragraph("Resumen Ejecutivo", estilos["titulo_seccion"]),
        HRFlowable(width="100%", thickness=1, color=COLOR_ACENTO),
        Spacer(1, 0.4 * cm),
        _tabla_con_estilo(kpis, col_anchos=[8 * cm, 5 * cm, 5 * cm]),
    ]

def _seccion_ingresos_por_hab(estilos: dict, m: MetricasNegocio) -> list:
    df = m.ingreso_anual_por_hab
    if df.empty:
        return [Paragraph("Sin datos de ingresos por habitación.", estilos["normal"])]

    encabezado = ["Habitación"] + [str(a) for a in df.columns] + ["Total"]
    filas = [encabezado]

    for hab in df.index:
        fila = [hab] + [f"S/ {df.loc[hab, año]:,.0f}" for año in df.columns]
        fila.append(f"S/ {df.loc[hab].sum():,.0f}")
        filas.append(fila)

    totales = ["TOTAL"]
    for año in df.columns:
        totales.append(f"S/ {df[año].sum():,.0f}")
    totales.append(f"S/ {df.values.sum():,.0f}")
    filas.append(totales)

    n_cols = len(encabezado)
    ancho_col = 16 * cm / n_cols

    return [
        Paragraph("Ingresos Anuales por Habitación", estilos["titulo_seccion"]),
        HRFlowable(width="100%", thickness=1, color=COLOR_ACENTO),
        Spacer(1, 0.4 * cm),
        _tabla_con_estilo(filas, col_anchos=[ancho_col] * n_cols, fila_total=True),
    ]

def _seccion_ocupacion(estilos: dict, m: MetricasNegocio) -> list:
    df = m.ocupacion_por_hab
    if df.empty:
        return [Paragraph("Sin datos de ocupación.", estilos["normal"])]

    encabezado = ["Habitación", "Meses ocupados", "Tasa de ocupación"]
    filas = [encabezado] + [
        [
            row[config.COL_HABITACION],
            str(int(row["meses_ocupados"])),
            f"{row['tasa_ocupacion_%']}%",
        ]
        for _, row in df.iterrows()
    ]

    return [
        Paragraph("Ocupación por Habitación (histórico)", estilos["titulo_seccion"]),
        HRFlowable(width="100%", thickness=1, color=COLOR_ACENTO),
        Spacer(1, 0.4 * cm),
        _tabla_con_estilo(filas, col_anchos=[7 * cm, 5 * cm, 5 * cm]),
    ]

def _seccion_graficas(estilos: dict, m: MetricasNegocio) -> list:
    elementos = [
        Paragraph("Gráficas", estilos["titulo_seccion"]),
        HRFlowable(width="100%", thickness=1, color=COLOR_ACENTO),
        Spacer(1, 0.4 * cm),
    ]

    img_ingresos = _grafica_ingresos_mensuales(m)
    if img_ingresos:
        elementos.append(Image(img_ingresos, width=16 * cm, height=8 * cm))
        elementos.append(Spacer(1, 0.5 * cm))

    img_ocupacion = _grafica_ocupacion_mensual(m)
    if img_ocupacion:
        elementos.append(Image(img_ocupacion, width=16 * cm, height=8 * cm))

    return elementos

def _grafica_ingresos_mensuales(m: MetricasNegocio) -> io.BytesIO | None:
    if not m.ingreso_por_mes:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    periodos = list(m.ingreso_por_mes.keys())
    ingresos = list(m.ingreso_por_mes.values())

    ax.fill_between(range(len(periodos)), ingresos, alpha=0.2, color="#048A81")
    ax.plot(range(len(periodos)), ingresos, color="#048A81", linewidth=2, marker="o", markersize=5)
    ax.set_xticks(range(len(periodos)))
    ax.set_xticklabels(periodos, rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S/ {x:,.0f}"))
    ax.set_title("Ingresos Mensuales — Negocio Completo", fontsize=13, fontweight="bold", color="#2E4057")
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def _grafica_ocupacion_mensual(m: MetricasNegocio) -> io.BytesIO | None:
    if not m.tasa_ocupacion_mensual:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    periodos = list(m.tasa_ocupacion_mensual.keys())
    tasas    = list(m.tasa_ocupacion_mensual.values())

    ax.bar(range(len(periodos)), tasas, color="#2E4057", alpha=0.8)
    ax.axhline(y=80, color="#E07A5F", linestyle="--", linewidth=1.5, label="Meta 80%")
    ax.set_xticks(range(len(periodos)))
    ax.set_xticklabels(periodos, rotation=45, ha="right", fontsize=8)
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_title("Tasa de Ocupación Mensual", fontsize=13, fontweight="bold", color="#2E4057")
    ax.legend()
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def _crear_estilos() -> dict:
    base = getSampleStyleSheet()
    return {
        "titulo_portada": ParagraphStyle(
            "titulo_portada", fontSize=28, textColor=COLOR_PRIMARIO,
            spaceAfter=12, alignment=1, fontName="Helvetica-Bold",
        ),
        "subtitulo_portada": ParagraphStyle(
            "subtitulo_portada", fontSize=14, textColor=COLOR_ACENTO,
            spaceAfter=8, alignment=1,
        ),
        "titulo_seccion": ParagraphStyle(
            "titulo_seccion", fontSize=14, textColor=COLOR_PRIMARIO,
            spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "normal": base["Normal"],
        "pie": ParagraphStyle("pie", fontSize=9, textColor=colors.grey, alignment=1),
    }

def _tabla_con_estilo(
    datos: list[list],
    col_anchos: list[float],
    fila_total: bool = False,
) -> Table:
    tabla = Table(datos, colWidths=col_anchos)

    estilo = TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("ALIGN",        (0, 0), (-1, 0), "CENTER"),
        ("FONTSIZE",     (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_GRIS]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ])

    if fila_total and len(datos) > 1:
        estilo.add("BACKGROUND",  (0, -1), (-1, -1), COLOR_CLARO)
        estilo.add("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold")
        estilo.add("TEXTCOLOR",   (0, -1), (-1, -1), COLOR_PRIMARIO)

    tabla.setStyle(estilo)
    return tabla

def _pie_pagina(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2.5 * cm, 1.2 * cm, config.NOMBRE_NEGOCIO)
    canvas.drawRightString(
        A4[0] - 2.5 * cm, 1.2 * cm,
        f"Página {doc.page} — Generado {datetime.now().strftime('%d/%m/%Y')}",
    )
    canvas.restoreState()
