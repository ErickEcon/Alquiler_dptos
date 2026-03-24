import urllib.request
import urllib.parse
import pandas as pd
import time

try:
    print("Test 1: Full data")
    data1 = urllib.parse.urlencode({
        'habitacion': 'B_P2_Habitación 1',
        'inquilino': 'Juan Carlos',
        'precio': 500.0,
        'fecha_inicio': '2024-03-01'
    }).encode()
    
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers): return fp
        http_error_303 = http_error_302

    opener = urllib.request.build_opener(NoRedirectHandler)
    opener.open(urllib.request.Request('http://localhost:8002/guardar', data=data1))
    
    time.sleep(1)
    
    print("Test 2: Optional missing")
    data2 = urllib.parse.urlencode({
        'habitacion': 'B_P2_Habitación 1',
        'inquilino': '',
        'precio': 550.0,
        'fecha_inicio': ''
    }).encode()
    opener.open(urllib.request.Request('http://localhost:8002/guardar', data=data2))
    
    time.sleep(1)
    df = pd.read_excel("data/registros.xlsx")
    print(df[df["Habitación/Dpto"] == "B_P2_Habitación 1"].to_string())

except Exception as e:
    print("Error:", e)
