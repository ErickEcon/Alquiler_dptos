---
name: automatizaciones-pymes
description: >
  Skill para crear automatizaciones Python orientadas a pequeñas y medianas empresas (PYMEs)
  que trabajan con archivos Excel para el seguimiento de sus actividades diarias. Genera código
  pythonic, comentado y listo para usar, usando librerías como openpyxl, pandas, fastapi,
  schedule, pydantic y otras según el caso. Úsala cuando el usuario mencione automatización,
  Excel, reportes automáticos, seguimiento de inventario, ventas, clientes, facturación,
  tareas programadas, APIs internas o cualquier flujo de trabajo repetitivo en una pequeña
  empresa. También activa esta skill cuando el usuario diga cosas como "quiero automatizar",
  "tengo un Excel que...", "necesito un script que...", "cómo puedo ahorrar tiempo con...",
  o cuando describa procesos manuales que podrían sistematizarse con Python.
---

# Automatizaciones para PYMEs con Python

Esta skill ayuda a crear automatizaciones Python bien estructuradas, con código pythonic
y comentado, para pequeñas empresas que aún dependen de Excel en sus operaciones diarias.

---

## 🚀 Paso 0 — Preguntar qué necesita el usuario

**Antes de generar cualquier código**, muestra este menú interactivo al usuario:

```
¿Qué quieres automatizar hoy?

  📊 1. Reportes automáticos desde Excel
         → Leer uno o varios .xlsx y generar resúmenes, gráficas o PDFs

  🛒 2. Gestión de inventario
         → Control de stock, alertas de quiebre, actualización de precios

  💰 3. Seguimiento de ventas y facturación
         → Consolidar ventas diarias, calcular totales, detectar anomalías

  👥 4. Base de datos de clientes (CRM simple)
         → Alta de clientes, historial de compras, segmentación básica

  📅 5. Tareas programadas (scheduler)
         → Ejecutar scripts automáticamente a ciertas horas o días

  🌐 6. API interna con FastAPI
         → Exponer datos de Excel como endpoints REST para otras apps

  📧 7. Envío automático de correos con reportes
         → Adjuntar Excel o PDF y enviar a una lista de destinatarios

  🔄 8. Limpieza y consolidación de archivos Excel
         → Unir múltiples hojas/archivos, limpiar duplicados, estandarizar formato

  🧩 9. Flujo personalizado (describe tu caso)
         → Cuéntame qué proceso manual quieres eliminar

Escribe el número o descríbeme tu caso con tus propias palabras.
```

Después de recibir la respuesta, haz **máximo 2-3 preguntas de aclaración** antes de generar el código.
No preguntes cosas que puedas asumir con sensatos defaults.

---

## 🧱 Stack tecnológico por caso de uso

| Caso                      | Librerías principales                              |
|---------------------------|----------------------------------------------------|
| Leer/escribir Excel       | `openpyxl`, `pandas`                               |
| Limpieza de datos         | `pandas`, `numpy`                                  |
| Gráficas                  | `matplotlib`, `seaborn`                            |
| Generación de PDFs        | `reportlab`, `fpdf2`                               |
| API REST                  | `fastapi`, `uvicorn`, `pydantic`                   |
| Tareas programadas        | `schedule`, `APScheduler`                          |
| Envío de correos          | `smtplib` (stdlib), `yagmail`                      |
| Validación de datos       | `pydantic`, `pandera`                              |
| Base de datos ligera      | `sqlite3` (stdlib), `sqlmodel`                     |
| Empaquetado/distribución  | `typer` (CLI), `python-dotenv` (configuración)     |

---

## 📐 Principios de código que SIEMPRE debe seguir

1. **Pythonic**: Usa comprensiones de lista, context managers (`with`), f-strings, dataclasses o pydantic models.
2. **Comentado**: Cada bloque de código lleva un comentario que explica el *por qué*, no solo el *qué*.
3. **Configurable**: Variables de entorno o archivo `config.py` para rutas, credenciales, parámetros.
4. **Manejo de errores**: `try/except` específicos con mensajes claros, nunca excepciones silenciosas.
5. **Tipado**: Usa `type hints` en todas las funciones.
6. **Modular**: Funciones pequeñas con una sola responsabilidad.
7. **Reproducible**: Incluir `requirements.txt` o sección de instalación.

---

## 🗂 Estructura de proyecto recomendada

Para proyectos de más de un script, sugiere esta estructura:

```
mi_automatizacion/
├── config.py           # Configuración centralizada (rutas, parámetros)
├── main.py             # Punto de entrada principal
├── requirements.txt    # Dependencias del proyecto
├── .env                # Variables de entorno (NO subir a git)
├── .gitignore
├── data/
│   ├── input/          # Archivos Excel de entrada
│   └── output/         # Reportes generados
├── src/
│   ├── __init__.py
│   ├── reader.py       # Lógica de lectura de Excel
│   ├── processor.py    # Transformaciones y cálculos
│   ├── reporter.py     # Generación de reportes/gráficas
│   └── notifier.py     # Envío de correos / alertas
└── tests/
    └── test_processor.py
```

---

## 📚 Referencias por módulo

- **Excel avanzado con openpyxl** → ver `references/excel_openpyxl.md`
- **Pandas para PYMEs** → ver `references/pandas_pymes.md`
- **FastAPI + Excel como backend** → ver `references/fastapi_excel.md`
- **Scheduler y automatización de tareas** → ver `references/scheduler.md`
- **Envío de correos con Python** → ver `references/email_sender.md`

Lee el archivo de referencia relevante antes de generar código para ese módulo.

---

## ✅ Checklist antes de entregar código

- [ ] ¿El código corre sin modificaciones en el caso más simple?
- [ ] ¿Hay un bloque `if __name__ == "__main__":` si es script?
- [ ] ¿Están todos los imports al inicio del archivo?
- [ ] ¿Las rutas de archivos son configurables (no hardcodeadas)?
- [ ] ¿Hay `requirements.txt` con versiones fijadas?
- [ ] ¿Los errores comunes (archivo no encontrado, hoja inexistente) están manejados?
- [ ] ¿Hay instrucciones de instalación y uso en comentarios o README?
