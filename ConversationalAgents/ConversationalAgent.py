from abc import ABC
import json
import re
from typing import Dict

class ConversationalAgent(ABC):
    def __init__(self, model:str):
        self.model = model

    def start(self):
        pass

    def ask(self, prompt: str)-> str:
        pass

    def clean_answer(self, answer: str) -> Dict:
        """
        Limpia la respuesta del modelo para eliminar caracteres innecesarios.
        Args:
            answer: Respuesta cruda del modelo.
        Returns:
            Respuesta limpia.
        """
        try:
            # Limpieza robusta (incluye casos con '```json' y '```' en líneas separadas)
            clean_response = re.sub(r'^```json|```$', '', answer.strip(), flags=re.DOTALL).strip()
            
            # Parsear y validar
            parsed = json.loads(clean_response)
            return parsed
        except json.JSONDecodeError as e:
            print(f"Error de JSON (posible respuesta corrupta): {e}")
            new_prompt = f"""El siguiente texto no es un JSON válido:
            {clean_response}
            Por favor, corrige el formato y devuelve solo un JSON válido, sin comentarios adicionales.
            """
            return self.clean_answer(self.ask(new_prompt))
        except Exception as e:
            print(f"Error inesperado: {e}")
            return {}