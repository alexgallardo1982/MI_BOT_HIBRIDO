from flask import Flask, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv(os.path.expanduser('~/mi_bot_hibrido/.env'))

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY   = os.getenv('GROQ_API_KEY')

if not TELEGRAM_TOKEN:
    print("ERROR: TELEGRAM_TOKEN no encontrado")
    exit(1)

TELEGRAM_API = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'
groq_client  = Groq(api_key=GROQ_API_KEY)

# Google Drive
try:
    print(f"GOOGLE_CREDENTIALS_JSON presente: {bool(os.getenv('GOOGLE_CREDENTIALS_JSON'))}")
    print(f"GOOGLE_TOKEN_PICKLE_B64 presente: {bool(os.getenv('GOOGLE_TOKEN_PICKLE_B64'))}")
    
    from modules.google_drive import GoogleDrive
    drive = GoogleDrive()
    print("✅ Google Drive conectado")
except Exception as e:
    print(f"❌ Drive no conectado: {e}")
    import traceback
    traceback.print_exc()
    drive = None

# Respuestas automaticas
respuestas = {}

def cargar_respuestas():
    global respuestas
    try:
        with open('data/respuestas.json', 'r', encoding='utf-8') as f:
            respuestas = json.load(f)
            print("Respuestas cargadas")
    except Exception as e:
        print(f"Error cargando respuestas: {e}")

def buscar_respuesta(texto):
    texto_limpio = texto.lower()
    for categoria, items in respuestas.items():
        for clave, item in items.items():
            for patron in item.get('patrones', []):
                if patron.lower() in texto_limpio:
                    return item.get('respuesta', ''), 'AUTOMATICA'
    return None, None

# Google Drive comandos
PALABRAS_DRIVE = [
    "mis archivos", "mis carpetas", "listar archivos",
    "listar carpetas", "estructura", "arbol",
    "busca ", "buscar ", "abrir "
]

def es_comando_drive(texto):
    t = texto.lower()
    return any(p in t for p in PALABRAS_DRIVE)

def comando_drive(texto):
    if not drive:
        return "Google Drive no esta conectado"

    t = texto.lower().strip()

    if "mis archivos" in t or "listar archivos" in t:
        archivos = drive.mis_archivos(10)
        if not archivos:
            return "No encontre archivos en tu Drive"
        resp = "Tus ultimos archivos:\n\n"
        for i, f in enumerate(archivos, 1):
            icono = "[Carpeta]" if 'folder' in f['mimeType'] else "[Archivo]"
            resp += f"{i}. {icono} {f['name']}\n{f['webViewLink']}\n\n"
        return resp

    elif "mis carpetas" in t or "listar carpetas" in t:
        carpetas = drive.mis_carpetas()
        if not carpetas:
            return "No encontre carpetas en tu Drive"
        resp = "Tus carpetas:\n\n"
        for i, c in enumerate(carpetas, 1):
            resp += f"{i}. {c['name']}\n{c['webViewLink']}\n\n"
        return resp

    elif t.startswith("busca ") or t.startswith("buscar "):
        termino = t.replace("busca ", "").replace("buscar ", "").strip()
        archivos = drive.buscar(termino)
        if not archivos:
            return f"No encontre archivos con: {termino}"
        resp = f"Resultados para '{termino}':\n\n"
        for i, f in enumerate(archivos, 1):
            icono = "[Carpeta]" if 'folder' in f['mimeType'] else "[Archivo]"
            resp += f"{i}. {icono} {f['name']}\n{f['webViewLink']}\n\n"
        return resp

    elif "estructura" in t or "arbol" in t:
        lineas = drive.estructura()
        if not lineas:
            return "Tu Drive esta vacio"
        resp = "Tu Google Drive:\n\n"
        resp += "\n".join(lineas[:25])
        if len(lineas) > 25:
            resp += f"\n\n... y {len(lineas)-25} elementos mas"
        return resp

    elif t.startswith("abrir "):
        nombre = t.replace("abrir ", "").strip()
        nombre_carpeta, archivos = drive.contenido_carpeta(nombre)
        if not nombre_carpeta:
            return f"No encontre carpeta: {nombre}"
        if not archivos:
            return f"La carpeta '{nombre_carpeta}' esta vacia"
        
        # Formato compacto con emoji
        resp = f"*{nombre_carpeta}* ({len(archivos)} archivos)\n\n"
        
        for i, f in enumerate(archivos[:15], 1):
            icono = "📁" if 'folder' in f['mimeType'] else "📄"
            link = f['webViewLink']
            resp += f"{i}. {icono} {f['name']} [🔗]({link})\n"
        
        if len(archivos) > 15:
            resp += f"\n...y {len(archivos) - 15} mas"
        
        return resp

    return None

# IA Groq
# IA Groq
def generar_respuesta_ia(texto):
    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un asistente util y amable. Responde brevemente en maximo 3 lineas."},
                {"role": "user", "content": texto}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=200,
        )
        return completion.choices[0].message.content.strip(), 'IA'
    except Exception as e:
        print(f"Error IA: {e}")
        return "Disculpa, no puedo responder ahora.", 'ERROR'

# Enviar a Telegram
# Enviar a Telegram
def enviar_a_telegram(chat_id, texto):
    try:
        if len(texto) > 4000:
            texto = texto[:4000] + "\n\n... (mensaje truncado)"
        url = f'{TELEGRAM_API}/sendMessage'
        print(f"URL: {url}")
        print(f"Chat ID: {chat_id}")
        print(f"Texto: {texto}")
        
        payload = {'chat_id': chat_id, 'text': texto, 'parse_mode': 'Markdown'}
        print(f"Payload: {payload}")
        
        r = requests.post(url, json=payload, timeout=15)
        print(f"Status code: {r.status_code}")
        print(f"Response: {r.text}")
        
        return r.status_code == 200
    except Exception as e:
        print(f"Error enviando: {e}")
        import traceback
        traceback.print_exc()
        return False

# Webhook
# Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print(f"\n{'='*50}")
        print("WEBHOOK RECIBIDO")
        print(f"{'='*50}")
        
        data = request.get_json()
        print(f"Data recibida: {data}")
        
        if not data or 'message' not in data:
            print("Sin mensaje en data")
            return jsonify({'ok': True}), 200

        msg     = data['message']
        chat_id = msg['chat']['id']
        texto   = msg.get('text', '')

        print(f"Chat ID: {chat_id}")
        print(f"Texto: {texto}")
        print(f"{'='*50}")

        respuesta = None

        # 1. Google Drive
        if es_comando_drive(texto):
            respuesta = comando_drive(texto)
            if respuesta:
                print("GOOGLE DRIVE")

        # 2. Automatica
        if not respuesta:
            respuesta, _ = buscar_respuesta(texto)
            if respuesta:
                print("AUTOMATICA")

        # 3. IA
        if not respuesta:
            respuesta, _ = generar_respuesta_ia(texto)
            print("IA")

        print(f"Respuesta: {respuesta[:100] if respuesta else 'NONE'}")
        
        if respuesta:
            enviar_a_telegram(chat_id, respuesta)
            print(f"Enviado correctamente")
        else:
            print("SIN RESPUESTA")

        return jsonify({'ok': True}), 200

    except Exception as e:
        print(f"ERROR EN WEBHOOK: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': True}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'drive': 'si' if drive else 'no'}), 200

if __name__ == '__main__':
    import os
    print("BOT INICIANDO...")
    cargar_respuestas()
    port = int(os.environ.get('PORT', 3000))
    print(f"Servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
