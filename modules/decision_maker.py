import random
from config import USAR_RESPUESTAS_AUTOMATICAS, USAR_IA

class DecisionHibrida:
    """
    Decide si usar respuesta automática o IA
    85% automático, 15% IA
    """
    
    def __init__(self):
        self.umbral_automatico = USAR_RESPUESTAS_AUTOMATICAS
    
    def decidir(self, texto):
        """
        Decide qué tipo de respuesta usar
        
        Returns:
            'AUTOMATICA' o 'IA'
        """
        numero_aleatorio = random.random()
        
        if numero_aleatorio < self.umbral_automatico:
            return 'AUTOMATICA'
        else:
            return 'IA'
    
    def cambiar_proporcion(self, automatico, ia):
        """
        Cambia la proporción de uso
        Ejemplo: cambiar_proporcion(0.9, 0.1) = 90% automático
        """
        if automatico + ia != 1.0:
            print("⚠️ Las proporciones deben sumar 1.0")
            return False
        
        self.umbral_automatico = automatico
        return True
