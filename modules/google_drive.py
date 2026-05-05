import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
BASE   = os.path.expanduser('~/mi_bot_hibrido')

class GoogleDrive:
    def __init__(self):
        self.service = None
        self.conectar()

    def conectar(self):
        creds       = None
        token_path  = f'{BASE}/token.pickle'
        creds_path  = f'{BASE}/google-credentials.json'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow  = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)
        print("Google Drive conectado")

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

    def buscar(self, nombre):
        try:
            results = self.service.files().list(
                q=f"name contains '{nombre}' and trashed=false",
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink)',
                pageSize=10
            ).execute()
            return results.get('files', [])
        except HttpError as e:
            print(f"Error buscar: {e}")
            return []

    def estructura(self, padre='root', nivel=0):
        if nivel > 1:
            return []
        try:
            results = self.service.files().list(
                q=f"'{padre}' in parents and trashed=false",
                fields='files(id, name, mimeType)',
                pageSize=15
            ).execute()
            items  = results.get('files', [])
            lineas = []
            indent = "  " * nivel
            for item in items:
                icono = "[+]" if 'folder' in item['mimeType'] else "[-]"
                lineas.append(f"{indent}{icono} {item['name']}")
                if 'folder' in item['mimeType']:
                    sub = self.estructura(item['id'], nivel + 1)
                    lineas.extend(sub)
            return lineas
        except HttpError as e:
            print(f"Error estructura: {e}")
            return []

    def contenido_carpeta(self, nombre_carpeta):
        try:
            # Buscar la carpeta por nombre
            results = self.service.files().list(
                q=f"name contains '{nombre_carpeta}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields='files(id, name)',
                pageSize=5
            ).execute()

            carpetas = results.get('files', [])

            if not carpetas:
                return None, []

            carpeta = carpetas[0]

            # Listar contenido de la carpeta encontrada
            contenido = self.service.files().list(
                q=f"'{carpeta['id']}' in parents and trashed=false",
                fields='files(id, name, mimeType, webViewLink)',
                pageSize=20,
                orderBy='name'
            ).execute()

            archivos = contenido.get('files', [])
            return carpeta['name'], archivos

        except HttpError as e:
            print(f"Error contenido_carpeta: {e}")
            return None, []
