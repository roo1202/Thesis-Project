from abc import ABC
import json
import re
from typing import Dict

class ConversationalAgent(ABC):
    def __init__(self, model:str):
        self.model = model

    def start(self):
        pass

    def ask(self, prompt: str):
        pass

    def clean_answer(self, answer: str) -> Dict:
        """
        Limpia la respuesta del modelo para eliminar caracteres innecesarios.
        Args:
            answer: Respuesta cruda del modelo.
        Returns:
            Respuesta limpia.
        """
        # try:
        #     # Limpiar la respuesta
        #     clean_response = (answer).strip()
        #     if clean_response.startswith("```json"):
        #         clean_response = clean_response[7:]
        #     if clean_response.endswith("```"):
        #         clean_response = clean_response[:-3]
                
        #     # Parsear JSON
        #     return json.loads(clean_response)
        # except (json.JSONDecodeError, KeyError) as e:
        #     print(f"Error limpiando respuesta: {e}")
        #     print(f"Respuesta recibida: {answer}")
        #     return {}
        try:
            # Limpieza robusta (incluye casos con '```json' y '```' en líneas separadas)
            clean_response = re.sub(r'^```json|```$', '', answer.strip(), flags=re.DOTALL).strip()
            
            # Parsear y validar
            parsed = json.loads(clean_response)
            return parsed
        except json.JSONDecodeError as e:
            print(f"Error de JSON (posible respuesta corrupta): {e}")
            print(f"Contenido problemático (50 chars alrededor del error):")
            error_pos = e.pos
            print(clean_response[max(0, error_pos-25):error_pos+25])  # Contexto del error
            return {}
        except Exception as e:
            print(f"Error inesperado: {e}")
            return {}