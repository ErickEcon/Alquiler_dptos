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
