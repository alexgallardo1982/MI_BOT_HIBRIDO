import json

class BuscadorRespuestas:
    """
    Busca respuestas automáticas en la base de datos
    """
    
    def __init__(self, archivo_json):
        self.archivo = archivo_json
        self.respuestas = self.cargar()
    
    def cargar(self):
        """Carga el JSON de respuestas"""
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando respuestas: {e}")
            return {}
    
    def buscar(self, texto):
        """
        Busca respuesta para el texto
        
        Returns:
            (respuesta, categoria) o (None, None)
        """
        texto_limpio = texto.lower().strip()
        
        for categoria, items in self.respuestas.items():
            for clave, item in items.items():
                patrones = item.get('patrones', [])
                
                for patron in patrones:
                    if patron.lower() in texto_limpio:
                        return item.get('respuesta', ''), clave
        
        return None, None
    
    def agregar_respuesta(self, categoria, clave, patrones, respuesta):
        """
        Agrega una nueva respuesta
        
        Ejemplo:
        agregar_respuesta('productos', 'notebook', 
                         ['notebook', 'laptop'], 
                         'Tenemos notebooks HP y Dell')
        """
        if categoria not in self.respuestas:
            self.respuestas[categoria] = {}
        
        self.respuestas[categoria][clave] = {
            'patrones': patrones,
            'respuesta': respuesta
        }
        
        self.guardar()
        return True
    
    def guardar(self):
        """Guarda cambios al JSON"""
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.respuestas, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error guardando respuestas: {e}")
            return False
    
    def listar_categorias(self):
        """Lista todas las categorías disponibles"""
        return list(self.respuestas.keys())
    
    def listar_respuestas(self, categoria):
        """Lista respuestas de una categoría"""
        return list(self.respuestas.get(categoria, {}).keys())
