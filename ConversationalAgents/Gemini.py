import json
import re
import time
from typing import Dict
from dotenv import load_dotenv
import os
from google.genai import types

load_dotenv()
api_key = os.getenv("API_KEY_GEMINI")
from google import genai
from ConversationalAgents.ConversationalAgent import ConversationalAgent

class Gemini (ConversationalAgent):
    def __init__(self, model : str = "gemini-2.0-flash-exp"):
        super().__init__(model)
        self.client = genai.Client(api_key=api_key)
        #print(self.client.models.list())
        

    def ask(self, prompt: str, temperature: float = 0.6) -> str:
        time.sleep(5)
        try:
            response = self.client.models.generate_content(
                    model= self.model, contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature)
            )
        except Exception as e:
            print(f"Error del servidor: {e}")
            time.sleep(5)
            return self.ask(prompt, temperature)
        if isinstance(response.text, str):
            return response.text
        else :
            time.sleep(5)
            return self.ask(prompt, temperature)
    
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
            Por favor, corrige el formato y devuelve solo un JSON válido, sin comentarios adicionales, sabiendo que está dando el siguiente error:
            {e}
            """
            return self.clean_answer(self.ask(new_prompt))
        except Exception as e:
            print(f"Error inesperado: {e}")
            return {}