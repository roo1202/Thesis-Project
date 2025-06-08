from enum import Enum
from typing import Dict, List, Optional
import json
from ConversationalAgents.ConversationalAgent import ConversationalAgent
from StorySpace.Character import Character
from StorySpace.Event import Event

class EventRelationType(Enum):
    """Tipos de relaciones entre eventos que pueden ocurrir en la historia"""
    TEMPORAL = "temporal"
    CAUSAL = "causal"

class Relationship:
    def __init__(self,
                 entity1: str,
                 entity2: str,
                 relationship_type: str):
        """
        Representa una relacion entre dos eventos

        Args:
        entity1: primer evento
        entity2: segundo evento
        relationship_type: relacion entre los eventos
        """
        self.entity1 = entity1
        self.entity2 = entity2
        self.relationship_type = relationship_type

    def to_dict(self) -> Dict:
        """Serializa la relación a un diccionario"""
        return {
            "entity1": self.entity1,
            "entity2": self.entity2,
            "relationship_type": self.relationship_type
        }
        

class EntityRelationship(Relationship):
    def __init__(self, 
                 entity1: str,
                 entity2: str,
                 relationship_type: str,
                 description: str,
                 strength: float = 1.0,  # 0.0 a 1.0
                 mutual: bool = True,
                 bidirectional: bool = False,
                 properties: Optional[Dict] = None):
        """
        Representa una relación entre dos entidades.
        
        Args:
            relationship_id: ID único de la relación
            entity1_id: ID de la primera entidad
            entity2_id: ID de la segunda entidad
            relationship_type: Tipo de relación (ej. 'amigos', 'enemigos', 'padre-hijo')
            description: Descripción de la relación
            strength: Intensidad de la relación (0.0 a 1.0)
            mutual: Si la relación es mutua (ambas partes la reconocen)
            bidirectional: Si la relación es bidireccional pero diferente en cada dirección
            properties: Propiedades adicionales de la relación
        """
        self.entity1 = entity1
        self.entity2 = entity2
        self.relationship_type = relationship_type
        self.description = description
        self.strength = max(0.0, min(1.0, strength))
        self.mutual = mutual
        self.bidirectional = bidirectional
        self.properties = properties or {}
        
    def to_dict(self) -> Dict:
        """Serializa la relación a un diccionario"""
        return {
            "entity1": self.entity1,
            "entity2": self.entity2,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "strength": self.strength,
            "mutual": self.mutual,
            "bidirectional": self.bidirectional,
            "properties": self.properties
        }

class RelationshipManager:
    def __init__(self, model: ConversationalAgent):
        """
        Gestiona relaciones entre entidades y puede inferir nuevas relaciones.
        
        Args:
            model: Modelo de agente conversacional que se empleará
        """
        self.relationships: Dict[str, Relationship] = {}
        self.entities: Dict[str, Dict] = {}
        self.model = model
        
    
    def add_entity(self, entity_id: str, entity_data: Dict):
        """Añade una entidad al manager"""
        self.entities[entity_id] = entity_data
    
    def add_entities(self, entities: Dict[str, Dict]):
        """Añade múltiples entidades al manager"""
        self.entities.update(entities)
    
    def add_relationship(self, relationship: Relationship):
        """Añade una relación al manager"""
        self.relationships[relationship.relationship_id] = relationship
    
    def get_relationships_for_entity(self, entity: str) -> List[Relationship]:
        """Obtiene todas las relaciones de una entidad"""
        return [rel for rel in self.relationships.values() 
                if entity in (rel.entity1, rel.entity2)]
    
    def get_relationship_between(self, entity1: str, entity2: str) -> Optional[Relationship]:
        """Obtiene la relación entre dos entidades específicas"""
        for rel in self.relationships.values():
            if (rel.entity1 == entity1 and rel.entity2 == entity2) or \
               (rel.entity1 == entity2 and rel.entity2 == entity1):
                return rel
        return None
    
    def infer_relationships_from_text(self,                       
                                    existing_entities: List[str],
                                    existing_events: List[Event],
                                    prompt_template: Optional[str] = None) -> List[Relationship]:
        """
        Infiere relaciones entre entidades a partir de un texto usando un modelo de lenguaje.
        
        Args:
            text: Texto del cual inferir relaciones
            existing_entities: Lista de entidades existentes
            prompt_template: Plantilla personalizada para el prompt
            
        Returns:
            Lista de relaciones inferidas
        """
        # Procesar eventos por chunks
        all_event_relations = []
        chunk_size = 10 if len(existing_events) > 50 else 5 
        overlap = 3 if len(existing_events) > 50 else 2
        
        # Dividir los eventos en chunks
        for event_chunk in self.chunk_events(existing_events, chunk_size, overlap):
            # Construir el prompt para el chunk actual de eventos
            events_relation_prompt = self._build_events_relationship_prompt(event_chunk)

            # Construir el prompt para entidades (si sigue siendo necesario)
            prompt = self._build_relationship_prompt(event_chunk, existing_entities, prompt_template)
            
            try:
                # Hacer la llamada a la API para el chunk actual
                response2 = self.model.ask(events_relation_prompt)
                
                # Procesar la respuesta del chunk actual
                chunk_relations = self._parse_events_relation_from_response(response2)
                all_event_relations.extend(chunk_relations)
                
            except Exception as e:
                print(f"Error al procesar chunk de eventos: {e}")
                continue
        
            try:
                # Procesar las relaciones de entidades
                response = self.model.ask(prompt)
                new_relationships = self._parse_relationships_from_response(response)
                
                # Combinar todas las relaciones
                all_event_relations.extend(new_relationships)
                
            except Exception as e:
                print(f"Error al inferir relaciones de entidades: {e}")
                return all_event_relations  # Devolver al menos las relaciones de eventos que sí se procesaron
            
        return all_event_relations
        
    def _build_events_relationship_prompt(self, events: List[Event]) -> str:
        """
        Construye el prompt para inferir las relaciones entre los eventos.
        """

        prompt = f"""
                Extract:
                {{
                    relationships: [
                    {{
                    "event1": "<titulo del primer evento>",
                    "event2": "<titulo del segundo evento>",
                    "relationship_type": "<Tipo de relación entre los eventos>"
                    }}
                }}
                In valid JSON format.
                Consider only the following events and relationships:
                Events:{[f"title:{event.title} descripription: {event.description}" for event in events]}
                Relationships:["causal" (event1 causa el event2), "prereq" (event1 es un prerrequisito para event2)]
                """
        
        return prompt

    def _build_relationship_prompt(self, 
                                 events: List[Event],
                                 entities: List[str],
                                 custom_template: Optional[str]) -> str:
        """
        Construye el prompt para inferir relaciones.
        """
  
        # Usar template personalizado o el default
        if custom_template:
            prompt = custom_template.format(entities_info="\n".join(entities))
        else:
            prompt = f"""
                Extract:
                {{
                relationships: [
                    {{
                    "entity1": "<primera entidad>",
                    "entity2": "<segunda entidad>",
                    "relationship_type": "<Tipo de relación (ej. 'amigos', 'enemigos')>",
                    "description": "<Descripción de la relación (ej. 'Kael y Lirien son amigos')>",
                    "mutual": <Si la relación es mutua (True/False)>,
                    "bidirectional": <Si la relación es bidireccional (True/False)>
                    }}
                }}
                In valid JSON format.
                Consider only the following entities:
                {[entity for entity in entities]}
                From the following text:
                ```{[event.description for event in events]}```
                """
        
        return prompt
    
    def _parse_relationships_from_response(self, response_text: str) -> List[EntityRelationship]:
        """
        Parsea la respuesta de Gemini a objetos Relationship.
        """
        try:
            # Limpiar la respuesta
            clean_response = response_text.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
                
            # Parsear JSON
            data = json.loads(clean_response)
            relationships_data = data.get("relationships", [])
            #print("Relaciones entre entidades:", json.dumps(data, indent=2, ensure_ascii=False))
            
            # Crear objetos Relationship
            new_relationships = []
            for rel_data in relationships_data:
                relationship = EntityRelationship(
                    entity1=rel_data["entity1"],
                    entity2=rel_data["entity2"],
                    relationship_type=rel_data["relationship_type"],
                    description=rel_data["description"],
                    mutual=bool(rel_data.get("mutual", True)),
                    bidirectional=bool(rel_data.get("bidirectional", False))
                )
                new_relationships.append(relationship)
            
            return new_relationships
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parseando relaciones: {e}")
            print(f"Respuesta recibida: {response_text}")
            return []
        
    def _parse_events_relation_from_response(self, response_text: str) -> List[Relationship]:
        """
        Parsea la respuesta de Gemini a objetos EventRelationship.
        """
        try:
            # Limpiar la respuesta
            clean_response = response_text.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
                
            # Parsear JSON
            data = json.loads(clean_response)
            relationships_data = data.get("relationships", [])
            #print("Relaciones entre eventos:", json.dumps(data, indent=2, ensure_ascii=False))
            
            # Crear objetos EventRelationship
            new_relationships = []
            for rel_data in relationships_data:
                relationship = Relationship(
                    entity1=rel_data["event1"],
                    entity2=rel_data["event2"],
                    relationship_type=rel_data["relationship_type"]     
                )
                new_relationships.append(relationship)
            
            return new_relationships
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parseando relaciones entre eventos: {e}")
            print(f"Respuesta recibida: {response_text}")
            return []
    

    def verify_subplot(self, events):
        prompt = f"""
        Evalúa si la siguiente secuencia de eventos forma un arco narrativo completo:
        {", ".join(e for e in events)}

        Responde en formato JSON con:
        - "completo": bool,
        - "faltantes": ["introducción", "conflicto", "resolución"],
        - "coherencia": 1-10
        """
        response = self.model.clean_answer(self.model.ask(prompt))
        return response
    

    def chunk_events(self, events, chunk_size=10, overlap=2):
        """Divide los eventos en chunks solapados para contexto continuo"""
        for i in range(0, len(events), chunk_size - overlap):
            yield events[i:i + chunk_size]