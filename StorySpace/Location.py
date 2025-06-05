from enum import Enum, auto
from typing import Dict, List, Optional
from StorySpace.Entity import Entity

class ClimateType(Enum):
    """Tipos de clima"""
    TEMPERATE = "templado"
    TROPICAL = "tropical"
    ARID = "árido"
    CONTINENTAL = "continental"
    POLAR = "polar"
    MEDITERRANEAN = "mediterráneo"
    TUNDRA = "tundra"
    MAGICAL = "mágico"  # Para climas alterados mágicamente

class Location (Entity):

    _name = "ubicaciones"
    _prompt = f"""{{
            name: Nombre de la ubicación
            description: Descripción detallada
            history: Breve historia del lugar
            dangers: Lista de peligros del lugar
            resources: Lista de recursos disponibles
            is_magical: (True/False) Si tiene propiedades mágicas
            is_secret: (True/False) Si es desconocida para la mayoría
            conexion: Lista de ubicaciones a las que se puede llegar
            }}
    """
    def __init__(self,
                 name: str,
                 description: str,
                 history: Optional[str] = None,
                 dangers: Optional[List[str]] = None,
                 resources: Optional[List[str]] = None,
                 is_magical: bool = False,
                 is_secret: bool = False,
                 conexion: Optional[List[str]] = None,
                 **kwargs):
        """
        Representa una ubicación en el mundo de la historia.
        
        Args:
            name: Nombre de la ubicación
            description: Descripción detallada
            history: Breve historia del lugar
            dangers: Peligros del lugar
            resources: Recursos disponibles
            is_magical: Si tiene propiedades mágicas
            is_secret: Si es desconocida para la mayoría
            conexion: Ubicaciones accesibles desde esta
        """
        self.name = name
        self.description = description
        self.history = history
        self.dangers = dangers or []
        self.resources = resources or []
        self.is_magical = is_magical
        self.is_secret = is_secret
        self.conexion = conexion  
        

    def description_summary(self) -> str:
        """
        Devuelve un resumen de la ubicación.
        
        Returns:
            str: Resumen de la descripción
        """
        return f"{self.name}: {self.description}..." if self.description else f"{self.name}: Sin descripción"

    
    
    def to_dict(self) -> Dict:
        """Serializa la ubicación a un diccionario"""
        return {
            "name": self.name,
            "description": self.description,
            "history": self.history,
            "dangers": self.dangers,
            "resources": self.resources,
            "is_magical": self.is_magical,
            "is_secret": self.is_secret,
            "conexion": self.conexion
        }


    def add_features(self, new_features: Dict[str, any]) -> None:
        """
        Actualiza los atributos de la ubicación con nuevos valores,
        evitando duplicados en listas y respetando valores existentes no vacíos.
        
        Args:
            new_features: Diccionario con campos a actualizar.
                         Ej: {"dangers": ["dragones"], "climate": "árido"}
        """
        for key, value in new_features.items():
            if not hasattr(self, key):
                print(f"La ubicación no tiene el atributo '{key}'")
                continue
            
            current_value = getattr(self, key)
            
            if isinstance(current_value, list) and isinstance(value, list):
                # Para listas (dangers, resources): añade solo elementos no existentes
                new_items = [item for item in value if item not in current_value]
                current_value.extend(new_items)
            
            elif isinstance(current_value, str) and current_value in ["", "normal"]:
                # Para strings vacíos o estado "normal": actualiza si el nuevo valor es válido
                if value:  # No actualiza si el valor es vacío
                    setattr(self, key, value)
            
            elif key in ["is_magical", "is_secret"]:
                # Para booleanos: sobrescribe siempre
                setattr(self, key, value)
            
            else:
                # Para otros casos (climate, size, etc.): sobrescribe
                setattr(self, key, value)