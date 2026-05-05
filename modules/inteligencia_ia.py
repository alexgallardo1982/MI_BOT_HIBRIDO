import openai
from config import OPENAI_API_KEY, TIMEOUT_IA

openai.api_key = OPENAI_API_KEY

class AsistenteIA:
    """
    Conecta con ChatGPT para preguntas complejas
    """
    
    def __init__(self):
        self.modelo = "gpt-3.5-turbo"
        self.temperatura = 0.7
        self.max_tokens = 150
    
    def generar_respuesta(self, pregunta, contexto=""):
        """
        Genera respuesta con IA
        
        Args:
            pregunta: Pregunta del usuario
            contexto: Información adicional
        
        Returns:
            Respuesta de IA o mensaje de error
        """
        try:
            prompt = f"""Eres un asistente útil y amable.
Contexto: {contexto if contexto else 'No hay contexto especial'}

Pregunta del usuario: {pregunta}

Responde de forma breve y útil en máximo 2 líneas."""
            
            respuesta = openai.ChatCompletion.create(
                model=self.modelo,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente amable para un negocio"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperatura,
                max_tokens=self.max_tokens,
                timeout=TIMEOUT_IA
            )
            
            return respuesta['choices'][0]['message']['content'].strip()
        
        except Exception as e:
            print(f"❌ Error con IA: {e}")
            return "Lo siento, no pude procesar tu pregunta en este momento. Intenta de nuevo."
    
    def cambiar_temperatura(self, valor):
        """
        Cambia la creatividad de la IA (0-1)
        Menor = más preciso, Mayor = más creativo
        """
        if 0 <= valor <= 1:
            self.temperatura = valor
            return True
        return False
