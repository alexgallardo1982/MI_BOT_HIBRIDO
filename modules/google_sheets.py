import os
import pickle
import base64
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SPREADSHEET_ID = "1D5btHr2F692qJtG5I_DbTyasKVXbzWoydB2EmNgcSdA"
SHEET_NAME = "Control_Documentos"

class GoogleSheets:
    def __init__(self):
        self.service = None
        self.datos = []
        self.conectar()
        self.cargar_datos()
    
    def conectar(self):
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
            print(f"❌ Error: {e}")
    
    def cargar_datos(self):
        try:
            if not self.service:
                return
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!A:H"
            ).execute()
            valores = result.get('values', [])
            if len(valores) < 2:
                return
            encabezados = valores[0]
            self.datos = []
            for fila in valores[1:]:
                while len(fila) < len(encabezados):
                    fila.append("")
                registro = {encabezados[i].lower(): fila[i] for i in range(len(encabezados))}
                self.datos.append(registro)
            print(f"✅ Sheets: {len(self.datos)} registros")
        except Exception as e:
            print(f"❌ Error cargando Sheets: {e}")
    
    def buscar_oc(self, numero):
        numero = str(numero).strip().lower()
        for reg in self.datos:
            if str(reg.get('oc', '')).strip().lower() == numero:
                return reg
        return None
    
    def resumen(self):
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
        
        texto = "📊 RESUMEN ÓRDENES DE COMPRA\n"
        texto += "=" * 50 + "\n\n"
        texto += f"📦 Total OCs: {total}\n"
        texto += f"💰 Monto Total: ${monto_total:,.0f}\n\n"
        texto += "DETALLE (Primeras 10):\n"
        texto += "-" * 50 + "\n\n"
        
        for i, reg in enumerate(self.datos[:10], 1):
            texto += f"{i}. OC {reg.get('oc', 'N/A')}\n"
            texto += f"   📅 Fecha: {reg.get('fecha de creación', 'N/A')}\n"
            texto += f"   🧾 Factura: {reg.get('factura', 'N/A')}\n"
            texto += f"   📄 GD: {reg.get('gd', 'N/A')}\n"
            texto += f"   ✉️ PE: {reg.get('pe', 'N/A')}\n"
            texto += f"   🪪 RUT: {reg.get('rut', 'N/A')}\n"
            texto += f"   🏢 Proveedor: {reg.get('nombre', 'N/A')}\n"
            texto += f"   💰 Monto: {reg.get('monto', 'N/A')}\n"
            texto += "\n"
        
        if total > 10:
            texto += f"... y {total - 10} más\n"
        
        texto += "\n" + "=" * 50
        return texto
    
    def formatear_oc(self, reg):
        texto = "📋 ORDEN DE COMPRA\n" + "=" * 50 + "\n\n"
        campos = {
            'fecha de creación': '📅',
            'oc': '📦',
            'factura': '🧾',
            'gd': '📄',
            'pe': '✉️',
            'rut': '🪪',
            'nombre': '🏢',
            'monto': '💰'
        }
        for campo, emoji in campos.items():
            valor = reg.get(campo, '')
            if valor:
                label = campo.replace('fecha de creación', 'Fecha').title()
                texto += f"{emoji} {label}: {valor}\n"
        return texto
    
    def buscar_proveedor_sin_factura(self, nombre_proveedor):
        nombre_proveedor = nombre_proveedor.lower().strip()
        resultados = []
        for reg in self.datos:
            prov = str(reg.get('nombre', '')).lower().strip()
            factura = str(reg.get('factura', '')).strip()
            if nombre_proveedor in prov and not factura:
                resultados.append(reg)
        return resultados
    
    def resumen_proveedor_sin_factura(self, nombre_proveedor):
        ocs = self.buscar_proveedor_sin_factura(nombre_proveedor)
        if not ocs:
            return f"❌ No hay OCs sin factura para: {nombre_proveedor}"
        
        total = len(ocs)
        monto_total = 0
        try:
            for oc in ocs:
                monto_str = str(oc.get('monto', '0')).replace('$', '').replace(',', '')
                monto_total += float(monto_str) if monto_str else 0
        except:
            pass
        
        texto = f"🔍 OCS SIN FACTURA - {nombre_proveedor.upper()}\n"
        texto += "=" * 60 + "\n\n"
        texto += f"📦 Total OCs sin factura: {total}\n"
        texto += f"💰 Monto Total: ${monto_total:,.0f}\n\n"
        texto += "DETALLE:\n"
        texto += "-" * 60 + "\n\n"
        
        for i, oc in enumerate(ocs[:20], 1):
            texto += f"{i}. OC {oc.get('oc', 'N/A')}\n"
            texto += f"   📅 Fecha: {oc.get('fecha de creación', 'N/A')}\n"
            texto += f"   📄 GD: {oc.get('gd', 'N/A')}\n"
            texto += f"   ✉️ PE: {oc.get('pe', 'N/A')}\n"
            texto += f"   🪪 RUT: {oc.get('rut', 'N/A')}\n"
            texto += f"   💰 Monto: {oc.get('monto', 'N/A')}\n"
            texto += "\n"
        
        if total > 20:
            texto += f"... y {total - 20} más\n"
        
        texto += "\n" + "=" * 60
        return texto
