from openai import OpenAI
from dotenv import load_dotenv
import os

from ConversationalAgents.ConversationalAgent import ConversationalAgent

load_dotenv()
api_key = os.getenv("API_KEY_DEEPSEEK")

from openai import OpenAI

class DeepSeek(ConversationalAgent):
    def __init__(self, system_prompt: str = "Eres un asistente útil", 
                 model: str = "deepseek/deepseek-r1:free", base_url: str = "https://api.deepseek.com",
                 proxies: dict = None, api_key: str = api_key):
        """
        Inicializa el cliente de DeepSeek.
        
        :param api_key: Tu API key de DeepSeek (OBLIGATORIO)
        :param system_prompt: Instrucción inicial para el modelo
        :param model: Nombre del modelo a usar
        :param base_url: URL base de la API
        :param proxies: Diccionario de proxies (opcional)
        """
        client_params = {
            'api_key': api_key,
            'base_url': base_url
        }
        
        self.client = OpenAI(**client_params)
        self.system_prompt = system_prompt
        self.model = model

    def ask(self, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Envía un prompt al modelo y devuelve la respuesta.
        
        :param user_prompt: Texto de la pregunta/comando
        :param temperature: Creatividad (0.0 a 1.0)
        :return: Respuesta del modelo como string
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=False
        )
        
        return response.choices[0].message.content

