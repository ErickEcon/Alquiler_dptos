import urllib.request
import urllib.parse
import pandas as pd
import time
import sys

try:
    print("Testing GET /")
    req = urllib.request.Request('http://localhost:8001/')
    with urllib.request.urlopen(req) as response:
        print("Status GET:", response.status)

    print("Testing POST /guardar")
    data = urllib.parse.urlencode({
        'habitacion': 'A_P1_Dpto. 1',
        'inquilino': 'Test Inquilino',
        'precio': 1200.5,
        'fecha_inicio': '2023-10-15'
    }).encode()
    
    # Catch redirect correctly
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            print("Redirect received (status", code, ") ->", headers['Location'])
            return fp
        http_error_303 = http_error_302

    opener = urllib.request.build_opener(NoRedirectHandler)
    with opener.open(urllib.request.Request('http://localhost:8001/guardar', data=data)) as response:
        print("Status POST:", response.status)
        
    time.sleep(1)
    
    print("\nReading data/registros.xlsx:")
    df = pd.read_excel("data/registros.xlsx")
    print(df.to_string())
    
except Exception as e:
    print("Exception during test:", e)
