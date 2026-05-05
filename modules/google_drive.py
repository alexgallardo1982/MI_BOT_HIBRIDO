import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
BASE = os.path.expanduser('~/mi_bot_hibrido')

class GoogleDrive:
    def __init__(self):
        self.service = None
        self.conectar()

    def conectar(self):
        creds = None
        token_path = os.path.expanduser('~/.ssh/token.pickle')
        creds_path = os.path.expanduser('~/.ssh/google-credentials.json')
        
        if not os.path.exists(creds_path):
            google_creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if google_creds_json:
                os.makedirs(os.path.dirname(creds_path), exist_ok=True)
                with open(creds_path, 'w') as f:
                    f.write(google_creds_json)
        
        if not os.path.exists(token_path):
            google_token_b64 = os.getenv('GOOGLE_TOKEN_PICKLE_B64')
            if google_token_b64:
                os.makedirs(os.path.dirname(token_path), exist_ok=True)
                token_data = base64.b64decode(google_token_b64)
                with open(token_path, 'wb') as f:
                    f.write(token_data)

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Google Drive conectado")

    def mis_archivos(self, limite=10):
        try:
            results = self.service.files().list(
                q="trashed=false",
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink, createdTime)',
                pageSize=limite,
                orderBy='createdTime desc'
            ).execute()
            return results.get('files', [])
        except HttpError as e:
            print(f"Error mis_archivos: {e}")
            return []

    def mis_carpetas(self):
        try:
            results = self.service.files().list(
                q="mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents",
                spaces='drive',
                fields='files(id, name, webViewLink)',
                pageSize=20
            ).execute()
            return results.get('files', [])
        except HttpError as e:
            print(f"Error mis_carpetas: {e}")
            return []

    def buscar(self, termino, limite=10):
        try:
            results = self.service.files().list(
                q=f"name contains '{termino}' and trashed=false",
                fields='files(id, name, mimeType, webViewLink)',
                pageSize=limite
            ).execute()
            return results.get('files', [])
        except HttpError as e:
            print(f"Error buscar: {e}")
            return []

    def estructura(self, carpeta_id='root', nivel=0):
        lineas = []
        try:
            results = self.service.files().list(
                q=f"'{carpeta_id}' in parents and trashed=false",
                fields='files(id, name, mimeType)',
                pageSize=50
            ).execute()
            items = results.get('files', [])
            for item in items[:10]:
                icono = '📁' if 'folder' in item['mimeType'] else '📄'
                lineas.append(f"{'  ' * nivel}{icono} {item['name']}")
                if 'folder' in item['mimeType'] and nivel < 2:
                    lineas.extend(self.estructura(item['id'], nivel + 1))
            return lineas
        except HttpError as e:
            print(f"Error estructura: {e}")
            return []

    def contenido_carpeta(self, nombre_carpeta):
        try:
            results = self.service.files().list(
                q=f"name contains '{nombre_carpeta}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields='files(id, name)',
                pageSize=5
            ).execute()
            carpetas = results.get('files', [])
            if not carpetas:
                return None, []
            carpeta = carpetas[0]
            contenido = self.service.files().list(
                q=f"'{carpeta['id']}' in parents and trashed=false",
                fields='files(id, name, mimeType, webViewLink)',
                pageSize=20,
                orderBy='name'
            ).execute()
            return carpeta['name'], contenido.get('files', [])
        except HttpError as e:
            print(f"Error contenido_carpeta: {e}")
            return None, []
