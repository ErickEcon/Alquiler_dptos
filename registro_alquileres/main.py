import os
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import gspread
from google.oauth2.service_account import Credentials

app = FastAPI(title="Registro de Alquileres (Cloud)")

# Inicialización de motor de plantillas Jinja2
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Lista de habitaciones
AVAILABLE_ROOMS = [
    "A_P1_Dpto. 1",
    "A_P2_Habitación 1",
    "A_P2_Habitación 2",
    "A_P2_Habitación 3",
    "A_P2_Habitación 4",
    "A_P3_MiniDpto 1",
    "A_P3_MiniDpto 2",
    "B_P1_Dpto 1",
    "B_P2_Habitación 1",
    "B_P2_Habitación 2",
    "B_P2_Habitación 3",
    "C_P1_Local 1",
    "C_P1_Local 2"
]

def get_google_sheet():
    """ Conecta con Google Sheets usando credentials.json """
    cred_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if not os.path.exists(cred_file):
        raise FileNotFoundError("ERROR CRÍTICO: Falta el archivo 'credentials.json' provisto por Google Cloud en la carpeta principal del proyecto.")
    
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(cred_file, scopes=scopes)
    client = gspread.authorize(creds)
    # Abre el documento "Alquileres Dptos" (debe estar compartido con el service account email)
    try:
        sheet = client.open("Alquileres Dptos").sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        raise Exception("No se encontró la hoja de cálculo llamada 'Alquileres Dptos'. Verifica que esté compartida con el bot.")
    return sheet

def save_to_google_sheets(habitacion: str, inquilino: str, precio: float, fecha_inicio: str, fecha_registro: str, metodo_pago: str):
    """
    Guarda un nuevo registro en Google Sheets con lógica de autocompletado en la nube.
    """
    sheet = get_google_sheet()
    
    try:
        all_records = sheet.get_all_records()
    except Exception:
        all_records = []
    
    if not inquilino or not fecha_inicio:
        # Filtrar registros previos por habitación
        prev_records = [r for r in all_records if r.get("Habitación/Dpto") == habitacion]
        
        if prev_records:
            ultimo = prev_records[-1]
            if not inquilino:
                inquilino = str(ultimo.get("Nombre del Inquilino", "No Registrado"))
            if not fecha_inicio:
                fecha_inicio = str(ultimo.get("Fecha de Inicio", "No Registrado"))
    
    if not inquilino: inquilino = "No Registrado"
    if not fecha_inicio: fecha_inicio = "No Registrado"
    
    # Si la hoja está verdaderamente vacía (sin cabeceras), las creamos
    if not all_records and len(sheet.get_all_values()) == 0:
        headers = ["Fecha de Registro", "Habitación/Dpto", "Nombre del Inquilino", "Precio Pagado", "Fecha de Inicio", "Método de Pago"]
        sheet.append_row(headers)
    
    new_row = [fecha_registro, habitacion, inquilino, precio, fecha_inicio, metodo_pago]
    sheet.append_row(new_row)

@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request, success: bool = False, error: str = ""):
    """
    Sirve el formulario HTML de la aplicación, inyectando las opciones y mensajes de error.
    """
    return templates.TemplateResponse(request=request, name="index.html", context={
        "rooms": AVAILABLE_ROOMS,
        "success": success,
        "error": error
    })

@app.post("/guardar")
async def process_form(
    habitacion: str = Form(...),
    inquilino: str = Form(default=""),
    precio: float = Form(...),
    fecha_inicio: str = Form(default=""),
    metodo_pago: str = Form(...)
):
    """
    Recibe los datos usando el método POST del formulario html, los manda a Google Sheets en la nube.
    """
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        save_to_google_sheets(habitacion, inquilino, precio, fecha_inicio, fecha_registro, metodo_pago)
        return RedirectResponse(url="/?success=true", status_code=303)
    except Exception as e:
        import urllib.parse
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"/?error={error_msg}", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
