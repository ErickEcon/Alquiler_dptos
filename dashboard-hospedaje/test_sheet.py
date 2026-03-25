import gspread
from google.oauth2.service_account import Credentials
creds = Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
client = gspread.authorize(creds)
doc = client.open_by_key('1z0GTn1LuX9GlkE1SHaWBeaIdbvORJuBORZ3IpVqRzQQ')
sheet = doc.worksheet('Hoja 1')
print(sheet.get_all_values())
