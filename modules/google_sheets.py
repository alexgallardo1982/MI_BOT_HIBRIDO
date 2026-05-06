"""
Google Sheets Module
Lee la hoja: HIT ESTATUS ORDENES DE COMPRA
"""

import os
import pickle
import base64
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SPREADSHEET_ID = "1D5btHr2F692qJtG5I_DbTyasKVXbzWoydB2EmNgcSdA"
SHEET_NAME = "Sheet1"

class GoogleSheets:
    def __init__(self):
        self.service = None
        self.datos = []
        self.conectar()
        self.cargar_datos()
    
    def conectar(self):
        """Conecta con Google Sheets"""
        try:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            creds = None
            token_path = os.path.expanduser('~/.ssh/token.pickle')
            
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
                    if creds.expired and creds.refresh_token:
                        creds.refresh(Request())
            
            if creds:
                self.service = build('sheets', 'v4', credentials=creds)
                print("✅ Google Sheets conectado")
        except Exception as e:
            print(f"❌ Error Sheets: {e}")
    
    def cargar_datos(self):
        """Carga datos de la hoja"""
        try:
            if not self.service:
                print("⚠️ Servicio Sheets no disponible")
                return
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!A:H"
            ).execute()
            
            valores = result.get('values', [])
            if len(valores) < 2:
                print("⚠️ Sheets vacío")
                return
            
            encabezados = valores[0]
            for fila in valores[1:]:
                while len(fila) < len(encabezados):
                    fila.append("")
                registro = {encabezados[i].lower(): fila[i] for i in range(len(encabezados))}
                self.datos.append(registro)
            
            print(f"✅ Sheets: {len(self.datos)} registros")
        except Exception as e:
            print(f"❌ Error cargando Sheets: {e}")
    
    def buscar_oc(self, numero):
        """Busca una OC"""
        numero = str(numero).strip().lower()
        for reg in self.datos:
            if str(reg.get('oc', '')).strip().lower() == numero:
                return reg
        return None
    
    def resumen(self):
        """Resumen de todas las OCs"""
        if not self.datos:
            return "❌ No hay datos en Sheets"
        
        total = len(self.datos)
        monto_total = 0
        
        try:
            for reg in self.datos:
                monto_str = str(reg.get('monto', '0')).replace('$', '').replace(',', '')
                monto_total += float(monto_str) if monto_str else 0
        except:
            pass
        
        texto = f"📊 RESUMEN OC\n{'='*30}\n"
        texto += f"📦 Total: {total}\n"
        texto += f"💰 Monto: ${monto_total:,.0f}\n\n"
        
        for i, reg in enumerate(self.datos[:5], 1):
            oc = reg.get('oc', 'N/A')
            proveedor = reg.get('nombre prooveedor', 'N/A')
            monto = reg.get('monto', 'N/A')
            texto += f"{i}. OC {oc}\n   {proveedor}\n   {monto}\n\n"
        
        if total > 5:
            texto += f"... +{total-5} más"
        
        return texto
    
    def formatear_oc(self, reg):
        """Formatea una OC para mostrar"""
        texto = "📋 ORDEN DE COMPRA\n" + "="*30 + "\n\n"
        
        campos = {
            'fecha': '📅',
            'oc': '📦',
            'factura': '🧾',
            'gd': '📄',
            'pe': '✉️',
            'rut': '🪪',
            'nombre prooveedor': '🏢',
            'monto': '💰'
        }
        
        for campo, emoji in campos.items():
            valor = reg.get(campo, '') or reg.get(campo.lower(), '')
            if valor:
                label = campo.replace('nombre prooveedor', 'Proveedor').title()
                texto += f"{emoji} {label}: {valor}\n"
        
        return texto
