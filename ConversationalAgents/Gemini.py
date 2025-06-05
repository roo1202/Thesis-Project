from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY_GEMINI")
from google import genai
from ConversationalAgents.ConversationalAgent import ConversationalAgent

class Gemini (ConversationalAgent):
    def __init__(self, model : str = "gemini-2.0-flash"):
        super().__init__(model)
        self.client = genai.Client(api_key=api_key)
        

    def ask(self, prompt: str):
        response = self.client.models.generate_content(
                model= self.model, contents=prompt
            )
        return response.text