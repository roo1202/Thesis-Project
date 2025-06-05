from typing import List, Dict, Optional, Union
from enum import Enum
from StorySpace.Entity import Entity

class CharacterRole(Enum):
    """Roles que pueden tener los personajes en un evento"""
    PROTAGONIST = "protagonista"
    ANTAGONIST = "antagonista"
    SUPPORTING = "secundario"
    NEUTRAL = "neutral"
    MENTOR = "mentor"
    COMIC_RELIEF = "alivio cómico"
    ENEMY = "enemigo"
    ALLY = "aliado"


class Character (Entity):

    _name = "personajes"
    _prompt = f"""{{
            name: Nombre del personaje
            role: Rol que cumple en la historia de los siguientes {[role.value for role in CharacterRole]}
            personality: Perfil de personalidad Big Five, cada uno del 0 a 100 {{
                "openness" :
                "conscientiousness":
                "extraversion":
                "agreeableness":
                "neuroticism":
            }}
            background: Historia de fondo del personaje
            appearance: Descripción física
            flaws: Lista de defectos o debilidades del personaje
            strengths: Lista de fortalezas o habilidades especiales
            }}
        """
    
    def __init__(self, 
                 name: str,
                 role: str,
                 personality: Dict,
                 background: str = "",
                 appearance: str = "",
                 motivations: Dict[str,str] = {},
                 goals: Dict[str,str] = {},
                 actions: Dict[str,str] = {},
                 flaws: Optional[List[str]] = None,
                 strengths: Optional[List[str]] = None,
                 **kwargs
                 ):
        """
        Representa un personaje en la historia con personalidad compleja
        
        Args:
            name: Nombre del personaje
            roles: Roles en la historia
            personality: Perfil de personalidad Big Five
            background: Historia de fondo del personaje
            appearance: Descripción física
            motivations: Lista de motivaciones principales
            goals: Objetivos del personaje
            flaws: Defectos o debilidades del personaje
            strengths: Fortalezas o habilidades especiales
        """
        self.name = name
        self.role = role
        self.personality = personality
        self.background = background
        self.appearance = appearance
        self.motivations = motivations or {}
        self.goals = goals or {}
        self.flaws = flaws or []
        self.strengths = strengths or []
        self.actions = actions or {}
        
        
    def description_summary(self) -> str:
        """
        Devuelve un resumen del personaje.
        
        Returns:
            str: Resumen de la descripción
        """
        return f"{self.name}: {self.role} - {self.background}..." if self.background else f"{self.name}: {self.role}"
    
    def to_dict(self) -> Dict:
        """Serializa el personaje a un diccionario"""
        return {
            "name": self.name,
            "role": self.role,
            "personality": {
                "openness": self.personality["openness"],
                "conscientiousness": self.personality["conscientiousness"],
                "extraversion": self.personality["extraversion"],
                "agreeableness": self.personality["agreeableness"],
                "neuroticism": self.personality["neuroticism"]
            },
            "background": self.background,
            "appearance": self.appearance,
            "flaws": self.flaws,
            "strengths": self.strengths
        }
    
    def add_features(self, new_features: Dict[str, any]) -> None:
        """
        Actualiza los atributos del personaje con nuevos valores,
        evitando duplicados en listas.
        
        Args:
            new_features: Diccionario con campos a actualizar.
                         Ej: {"strengths": ["manejo de arco"], "appearance": "Ojos verdes"}
        """
        for key, value in new_features.items():
            if not hasattr(self, key):
                print(f"El personaje no tiene el atributo '{key}'")
                continue
            
            current_value = getattr(self, key)
            
            if isinstance(current_value, list) and isinstance(value, list):
                # Para listas: añade solo elementos no existentes
                new_items = [item for item in value if item not in current_value]
                current_value.extend(new_items)
            elif isinstance(current_value, str) and isinstance(value, str) and value not in current_value:
                setattr(self, key, current_value + ', ' + value)
            elif key == 'personality':
                # Actualiza atributos de personalidad
                for sub_key, sub_value in value.items():
                    if hasattr(self.personality, sub_key):
                        self.personality[sub_key] = (sub_value + self.personality[sub_key])/2
            

    def __str__(self) -> str:
        """Representación en string del personaje, mostrando todos sus atributos clave"""
        # Encabezado con nombre y rol
        output = [f"╔{'═' * (len(self.name) + 2)}╗",
                f"║ {self.name.upper()} ║",
                f"╚{'═' * (len(self.name) + 2)}╝",
                f"Rol: {self.role}",
                ""]
        
        # Sección de descripción básica
        if self.background or self.appearance:
            output.append("─" * 40)
            output.append("📖 DESCRIPCIÓN")
            if self.background:
                output.append(f"  · Trasfondo: {self.background}")
            if self.appearance:
                output.append(f"  · Apariencia: {self.appearance}")
        
        # Sección de personalidad
        if self.personality:
            output.append("🧠 PERSONALIDAD")
            for trait, description in self.personality.items():
                output.append(f"  · {trait}: {description}")
        
        # Sección de motivaciones y metas
        if self.motivations or self.goals:
            output.append("🎯 MOTIVACIONES Y METAS")
            for motivation, desc in self.motivations.items():
                output.append(f"  · Evento : '{motivation}' Motivación: {desc}")
            for goal, desc in self.goals.items():
                output.append(f"  · Evento: '{goal}' Meta: {desc}")
        
        # Sección de acciones relevantes
        if self.actions:
            output.append("⚡ ACCIONES DESTACADAS")
            for action, desc in self.actions.items():
                output.append(f"  · {action}: {desc}")
        
        # Sección de fortalezas y debilidades
        if self.strengths or self.flaws:
            output.append("⚖️ FORTALEZAS Y DEBILIDADES")
            if self.strengths:
                output.append("  · Fortalezas:")
                for strength in self.strengths:
                    output.append(f"    - {strength}")
            if self.flaws:
                output.append("  · Debilidades:")
                for flaw in self.flaws:
                    output.append(f"    - {flaw}")
        
        # Atributos adicionales (kwargs)
        if hasattr(self, 'additional_attributes') or any(k for k in vars(self) if k not in [
            'name', 'role', 'personality', 'background', 'appearance',
            'motivations', 'goals', 'actions', 'flaws', 'strengths'
        ]):
            output.append("📌 ATRIBUTOS ADICIONALES")
            for attr, value in vars(self).items():
                if attr not in [
                    'name', 'role', 'personality', 'background', 'appearance',
                    'motivations', 'goals', 'actions', 'flaws', 'strengths'
                ] and not attr.startswith('_'):
                    output.append(f"  · {attr.replace('_', ' ').title()}: {value}")
        
        return "\n".join(output)