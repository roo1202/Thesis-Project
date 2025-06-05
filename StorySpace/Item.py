from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass
from StorySpace.Entity import Entity

class ItemType(Enum):
    """Tipos de ítems posibles en la historia"""
    ANIMAL = 'animal'
    # ARTIFACT = auto()      # Objeto creado por el hombre
    FOOD = 'comida'
    PLANT = 'planta'
    OBJECT = 'objeto'       # Objetos naturales no creados por el hombre
    CLOTHING = 'ropa'      # Ropa y vestimenta
    WEAPON = 'arma'        # Armas
    TOOL = 'herramienta'          # Herramientas
    JEWELRY = 'joyería'       # Joyas y adornos
    DOCUMENT = 'documento'      # Cartas, libros, mapas
    MAGICAL = 'objeto mágico'       # Objetos con propiedades mágicas
    CONTAINER = 'contenedor'     # Bolsas, cofres, recipientes

class ItemRarity(Enum):
    """Rareza del objeto"""
    COMMON = "común"
    UNCOMMON = "poco común"
    RARE = "raro"
    EPIC = "épico"
    LEGENDARY = "legendario"
    UNIQUE = "único"

@dataclass
class ItemEffect:
    """Posibles efectos que puede tener un ítem"""
    description: str
    #potency: int = 1  # 1-10, intensidad del efecto
    duration: Optional[str] = None  # "Permanente", "Temporal", etc.


class Item (Entity):

    _name = "ítems"
    _prompt = f"""{{
            name: Nombre del ítem
            item_type: Tipo de ítem entre los siguientes: {[item_type.value for item_type in ItemType]}
            description: Descripción detallada del ítem
            effects: Lista de efectos especiales que produce el ítem
            properties: Lista de características adicionales del ítem
            is_movable: (True/False) Si puede ser llevado por personajes
            is_consumable: (True/False) Si se destruye/usas al utilizarlo
            is_equippable: (True/False) Si puede ser equipado (armadura, armas, etc.)
            required_skills: Lista de habilidades necesarias para usar el ítem efectivamente
            }}
        """
    def __init__(self,
                 name: str,
                 item_type: str,
                 description: str,
                 effects: Optional[List[str]] = None,
                 properties: Optional[List[str]] = None,
                 is_movable: bool = False,
                 is_consumable: bool = False,
                 is_equippable: bool = False,
                 required_skills: Optional[List[str]] = None,
                 **kwargs):
        """
        Representa un ítem en el mundo de la historia.
        
        Args:
            name: Nombre del ítem
            item_type: Tipo de ítem (animal, artefacto, etc.)
            description: Descripción detallada del ítem
            effects: Efectos especiales que produce el ítem
            properties: Características adicionales del ítem
            is_movable: Si puede ser llevado por personajes
            is_consumable: Si se destruye/usas al utilizarlo
            is_equippable: Si puede ser equipado (armadura, armas, etc.)
            required_skills: Habilidades necesarias para usar el ítem efectivamente
        """
        self.name = name
        self.item_type = item_type
        self.description = description
        self.effects = effects or []
        self.properties = properties or []
        self.is_movable = is_movable
        self.is_consumable = is_consumable
        self.is_equippable = is_equippable
        self.required_skills = required_skills or []

        
    def description_summary(self) -> str:
        """
        Devuelve un resumen del ítem.
        
        Returns:
            str: Resumen
        """
        return f"{self.name}: {self.description}..." if self.description else f"{self.name}: Sin descripción"

    def use(self) -> str:
        """Simula el uso del ítem y devuelve un mensaje descriptivo"""
        if self.durability is not None and self.current_durability is not None:
            self.current_durability -= 1
            if self.current_durability <= 0:
                return f"El {self.name} se ha roto o consumido completamente."
        
        if self.effects:
            effect_desc = " ".join(effect.description for effect in self.effects)
            return f"Usas {self.name}. {effect_desc}"
        return f"Usas {self.name}, pero no parece tener ningún efecto especial."
    
    def inspect(self) -> str:
        """Devuelve una descripción detallada del ítem"""
        details = [
            f"Nombre: {self.name}",
            f"Tipo: {self.item_type.name.lower()}",
            f"Descripción: {self.description}",
            f"Rareza: {self.rarity.value}",
            f"Tamaño: {self.size}",
            f"Valor: {self.value} monedas",
        ]
        
        if self.durability is not None:
            details.append(f"Durabilidad: {self.current_durability}/{self.durability}")
        
        if self.effects:
            effects = "\n  - ".join(effect.description for effect in self.effects)
            details.append(f"Efectos:\n  - {effects}")
        
        if self.properties:
            props = "\n  - ".join(f"{k}: {v}" for k, v in self.properties.items())
            details.append(f"Propiedades:\n  - {props}")
            
        return "\n".join(details)
    
    def to_dict(self) -> Dict:
        """Serializa el ítem a un diccionario"""
        return {
            "name": self.name,
            "item_type": self.item_type,
            "description": self.description,
            "effects": self.effects,
            "properties": self.properties,
            "is_movable": self.is_movable,
            "is_consumable": self.is_consumable,
            "is_equippable": self.is_equippable,
            "required_skills": self.required_skills
        }
    

    def add_features(self, new_features: Dict[str, any]) -> None:
        """
        Actualiza los atributos del ítem con nuevos valores,
        evitando duplicados en listas y respetando valores existentes no vacíos.
        
        Args:
            new_features: Diccionario con campos a actualizar.
                         Ej: {"effects": ["invisibilidad"], "value": 50}
        """
        for key, value in new_features.items():
            if not hasattr(self, key):
                print(f"El ítem no tiene el atributo '{key}'")
                continue
            
            current_value = getattr(self, key)
            
            if isinstance(current_value, list) and isinstance(value, list):
                # Para listas (effects, required_skills): añade solo elementos no existentes
                new_items = [item for item in value if item not in current_value]
                current_value.extend(new_items)
            
            elif isinstance(current_value, dict) and isinstance(value, dict):
                # Para diccionarios (properties): actualiza/combina valores
                current_value.update(value)
            
            elif isinstance(current_value, (str, int, float)) and current_value in ["", 0, 0.0]:
                # Para campos vacíos/cero: actualiza si el nuevo valor no es neutro
                if value not in ["", 0, 0.0]:
                    setattr(self, key, value)
            
            elif key in ["is_movable", "is_consumable", "is_equippable"]:
                # Para booleanos: sobrescribe siempre
                setattr(self, key, value)
            
            else:
                # Para otros casos (rarity, size, etc.): sobrescribe
                setattr(self, key, value)


    def __str__(self):
        """Representación detallada del objeto con formato visual"""
        # Encabezado con nombre y tipo
        header = f"╔{'═' * (len(self.name) + 2)}╗\n║ {self.name.upper()} ║\n╚{'═' * (len(self.name) + 2)}╝"
        type_line = f"📦 TIPO: {self.item_type}"
        
        # Sección de descripción
        desc_section = f"\n📝 DESCRIPCIÓN:\n  {self.description}"
        
        # Sección de propiedades y estado
        properties = [
            f"🏷️ PROPIEDADES: {', '.join(self.properties) if self.properties else 'Ninguna'}",
            f"⚡ EFECTOS: {', '.join(self.effects) if self.effects else 'Ninguno'}",
            f"🛠️ HABILIDADES REQUERIDAS: {', '.join(self.required_skills) if self.required_skills else 'Ninguna'}"
        ]
        
        # Sección de flags (estados booleanos)
        flags = []
        if self.is_movable:
            flags.append("📦 Movible")
        if self.is_consumable:
            flags.append("🍶 Consumible")
        if self.is_equippable:
            flags.append("🛡️ Equipable")
        
        flags_section = "\n🚩 CARACTERÍSTICAS:\n  " + (" | ".join(flags) if flags else "Ninguna especial")
        
        # Construcción final
        return "\n".join([
            header,
            type_line,
            desc_section,
            "\n".join(properties),
            flags_section
        ])