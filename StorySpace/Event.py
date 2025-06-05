from dataclasses import asdict, dataclass, field
import json
from typing import List, Dict, Optional, Union
from dataclasses_json import dataclass_json
from StorySpace.Entity import Entity
from datetime import datetime


@dataclass
class Event(Entity):
    title: str = "Sin título"  
    description: str = "Descripción pendiente"
    locations: List[str] = field(default_factory=lambda: ["Lugar desconocido"])  
    timestamp: Union[str, datetime] = "día 0" 
    characters_involved: List[str] = field(default_factory=list)
    items_involved: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    is_mandatory: bool = False
    narrative_part : str = ""
    plot_part : str = ""

    _name = "eventos"
    _prompt = f"""{{
        title: Descripción muy breve del evento
        description: Descripción detallada del evento, con elementos narrativos
        locations: Lista de ubicaciones mencionadas en el evento, comenzando por el lugar donde se desarrolla
        timestamp: Tiempo dentro de la historia en el que se desarrolla el evento
        characters_involved: Lista de personajes involucrados
        items_involved: Lista de objetos o elementos involucrados
        effects: Lista de cambios que produce este evento
        is_mandatory: True si pertenece a la trama principal, False si es una subtrama
        narrative_part: inicio/desarrollo/fin de una trama según su significado
        plot_part: parte de la estructura narrativa en la que se clasificaría (depende de la estructura)
        }}
    """

    def to_json(self) -> json:
        """
        Convierte el evento a un json.
        
        Returns:
            json: Representación del evento como un json
        """
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def to_dict(self) -> Dict:
        """
        Convierte el evento a un diccionario para facilitar su serialización.
        
        Returns:
            dict: Representación del evento como un diccionario
        """
        return {
            "title": self.title,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "prerequisites": self.prerequisites,
            "effects": self.effects
        }
    
    def __str__(self) -> str:
        # Formatear el timestamp si es un objeto datetime
        timestamp_str = (self.timestamp.strftime("%Y-%m-%d %H:%M") 
                        if isinstance(self.timestamp, datetime) 
                        else str(self.timestamp))
        
        # Listas que pueden estar vacías
        def format_list(items: List[str], empty_msg: str = "Ninguno") -> str:
            return "\n  - " + "\n  - ".join(items) if items else f" {empty_msg}"
        
        # Construir el string
        return f"""
            {'='*10}
            Evento: {self.title}
            {'='*10}
            • Descripción: {self.description}
            • Ubicación(es):{format_list(self.locations)}
            • Momento: {timestamp_str}
            • Personajes involucrados:{format_list(self.characters_involved)}
            • Objetos involucrados:{format_list(self.items_involved)}
            • Prerrequisitos:{format_list(self.prerequisites)}
            • Efectos:{format_list(self.effects)}
            • ¿Es obligatorio?: {'Sí' if self.is_mandatory else 'No'}
            • Parte narrativa: {self.narrative_part or "No especificada"}
            • Parte del plot: {self.plot_part or "No especificada"}
            {'='*10}
            """.strip()
    
    
    def add_features(self, new_features: Dict[str, any]) -> None:
        """
        Actualiza los atributos del evento con nuevos valores,
        evitando duplicados en listas y respetando valores por defecto.
        
        Args:
            new_features: Diccionario con campos a actualizar.
                         Ej: {"locations": ["Bosque"], "effects": {"suspense": 2}}
        """
        for key, value in new_features.items():
            if not hasattr(self, key):
                print(f"El evento no tiene el atributo '{key}'")
                continue
            
            current_value = getattr(self, key)
            
            if isinstance(current_value, list) and isinstance(value, list):
                # Para listas: añade solo elementos no existentes
                new_items = [item for item in value if item not in current_value]
                current_value.extend(new_items)
            
            
            elif isinstance(current_value, str):
                setattr(self, key, value)
            
            
            elif key in ['is_mandatory']:
                # Para booleanos/float: sobrescribe
                setattr(self, key, value)
            