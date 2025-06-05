from typing import Dict, List
import json
from StorySpace.Entity import Entity
from ConversationalAgents.ConversationalAgent import ConversationalAgent
from StorySpace.Event import Event


class EntityRecognition:
    def __init__(self, model: ConversationalAgent):
        """
        Inicializa el reconocedor de entidades usando la API de Gemini.
        
        Args:
            api_key: Clave API de Google Gemini
            model_name: Nombre del modelo a usar (por defecto "gemini")
        """
        self.model = model

        
    def extract_entities(self, text: str, entity_types: List[Entity]) -> Dict:
        """
        Extrae entidades de un texto narrativo usando Gemini.
        
        Args:
            text: Texto narrativo del que extraer entidades
            entity_types: Lista de tipos de entidades a extraer (ej: ["character", "item", "event"])
            
        Returns:
            Diccionario con las entidades reconocidas organizadas por tipo
        """
        
        prompt = self._build_entity_extraction_prompt(text, entity_types)
        
        try:
            response = self.model.ask(prompt)
            return self._parse_response(response, entity_types)
            
        except Exception as e:
            print(f"Error al llamar a la API de Gemini: {e}")
            return {"error": str(e)}
    

    def _build_entity_extraction_prompt(self, text: str, entity_types: List[Entity]) -> str:
        """
        Construye el prompt para la extracción de entidades.
        """
        prompt_parts = [
            "Extract:"
        ]
        
        # Añadir instrucciones de formato personalizadas
        for entity in entity_types:
            prompt_parts.append(f"{entity._name}:{entity._prompt}\n")

    
        prompt_parts.append(
            "In valid JSON format. You can name and add whatever you want to the entities if it is not specified in the text. \n"
        )
        
        # Añadir el texto a analizar
        prompt_parts.append(f"From the following text::\n```{text}```\n\n")
        
        
        return "".join(prompt_parts)
    
    def _parse_response(self, response_text: str, entity_types: List[Entity]) -> Dict:
        """
        Parsea la respuesta de Gemini a un diccionario estructurado.
        """
        try:
            # Limpiar la respuesta (Gemini a veces añade marcas ```json)
            clean_response = response_text.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
                
            # Parsear a JSON
            entities = json.loads(clean_response)
            print("Entidades:", json.dumps(entities, indent=2, ensure_ascii=False))
            
            # Validar que contiene las claves esperadas
            for entity_type in entity_types:
                if entity_type._name not in entities:
                    entities[entity_type._name] = []
                    
            return entities
            
        except json.JSONDecodeError as e:
            print(f"Error parseando la respuesta JSON: {e}")
            print(f"Respuesta recibida: {response_text}")
            return {"error": "Invalid JSON response", "raw_response": response_text}
    

    def identify_entities(self, events: List[Event], entities: List[Entity]) -> str: 
        """
        Identifica entidades dadas en un texto narrativo.
        
        Args:
            text: Texto narrativo del que identificar entidades
            entities: Lista de entidades a identificar
            
        Returns:
            Diccionario con las entidades identificadas organizadas
        """
        prompt = f"""
        Replace characters, locations, and items in events according to their descriptions, and extract with the description changed and the fields updated:
        {{
            events: {{[
                {{
                    {Event._prompt}
                }},]
            }}
        }}
        In valid JSON format, considering only the following entities:
        {[entity.to_dict() for entity in entities]}
        The events to be analyzed are the following:
        {[event.to_dict() for event in events]}
        """

        try:
            response = self.model.ask(prompt)
            return response
            
        except Exception as e:
            print(f"Error al llamar a la API de Gemini: {e}")
            return {"error": str(e)}