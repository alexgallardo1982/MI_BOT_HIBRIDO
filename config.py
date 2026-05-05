import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
DEBUG = True
PORT = 3000
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Porcentajes de uso
USAR_RESPUESTAS_AUTOMATICAS = 0.85  # 85% respuestas automáticas
USAR_IA = 0.15  # 15% preguntas con IA

# Tiempo máximo de respuesta IA
TIMEOUT_IA = 10
