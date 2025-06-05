import os
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List
from StorySpace.Character import Character
from StorySpace.Event import Event
from pyvis.network import Network

from StorySpace.Item import Item


class GraphGenerator:
    def __init__(self):
        """Inicializa el generador de grafo de historia"""
        self.graph = nx.MultiDiGraph()
        self.events : Dict[str, Event] = {}
        self.event_counter = 1
        self.relationships = {}

    def add_event(self, event: Event):
        """
        Añade un evento al generador y crea las relaciones necesarias.
        
        Args:
            event: Instancia de la clase Event que contiene la información del evento
        """
        # Añadir el evento al diccionario
        self.events[event.title] = event
        
        # Añadir nodo al grafo
        self.graph.add_node(event.title,title=event.__str__(), node_type = "event")


    def add_character(self, character: Character):
        """
        Añade un personaje como nodo al grafo.
        
        Args:
            name: Nombre del personaje (identificador único)
            attributes: Diccionario con atributos adicionales del personaje
                       (ej: {"rol": "protagonista", "edad": 30})
        """
        # Añadir nodo al grafo con atributos y tipo diferenciado
        self.graph.add_node(character.name, 
                          node_type="character",
                          title=character.__str__())  


    def add_item(self, item: Item):
        """
        Añade un personaje como nodo al grafo.
        
        Args:
            name: Nombre del personaje (identificador único)
            attributes: Diccionario con atributos adicionales del personaje
                       (ej: {"rol": "protagonista", "edad": 30})
        """
        # Añadir nodo al grafo con atributos y tipo diferenciado
        self.graph.add_node(item.name, 
                          node_type="item",
                          title=item.__str__())  


    def link_character_to_events(self, character_name: str, event_relations: Dict[str, str]):
        """
        Relaciona un personaje con eventos existentes mediante aristas.
        
        Args:
            character_name: Nombre del personaje (debe existir)
            event_relations: Diccionario donde:
                            - clave: nombre del evento (debe existir)
                            - valor: descripción de la relación (ej: "participó", "causó")
        """
        if character_name not in self.graph.nodes:
            raise ValueError(f"El personaje '{character_name}' no existe")
        
        for event_name, relation_desc in event_relations.items():
            if event_name not in self.events:
                raise ValueError(f"El evento '{event_name}' no existe")
            
            # Añadir arista con descripción de relación
            self.graph.add_edge(
                character_name,
                event_name,
                relation=relation_desc
            )
            
        
    def link_item_to_event(self, item_name: str, event:str):
        """
        Relaciona un item con eventos existentes mediante aristas.
        
        Args:
            item_name: Nombre del item (debe existir)
            event: Nombre del evento en el que aparece(debe existir)
        """
        if item_name not in self.graph.nodes:
            raise ValueError(f"El item '{item_name}' no existe")
        
       
        if event not in self.events:
            raise ValueError(f"El evento '{event}' no existe")
        
        # Añadir arista con descripción de relación
        self.graph.add_edge(
            item_name,
            event,
            relation="appears_in",
        )

    def add_prereq_relation(self, event1:str, event2:str):
        """
        Establece una relación de prerrequisito entre dos eventos

        Args:
        event1: evento que debe ocurrir primero
        event2: evento que ocurre necesariamnete después del primero
        """
        if event1 in self.events and event2 in self.events:
            self.graph.add_edge(event1, event2, relation="prerequisite", label="prereq")
    
    def add_temporal_relation(self, earlier_event: str, later_event: str):
        """
        Establece una relación temporal entre dos eventos.
        
        Args:
            earlier_event: evento que ocurre primero
            later_event: evento que ocurre después
        """
        if earlier_event in self.events and later_event in self.events:
            self.graph.add_edge(earlier_event, later_event, relation="temporal", label="temporal")
    
    def add_causal_relation(self, cause_event: str, effect_event: str):
        """
        Establece una relación causal entre dos eventos.
        
        Args:
            cause_event: evento que causa
            effect_event: evento resultante
        """
        if cause_event in self.events and effect_event in self.events:
            self.graph.add_edge(cause_event, effect_event, relation="causal", label="causa")
    
    def validate_event_sequence(self, sequence: List[str]) -> Dict:
        """
        Valida si una secuencia de eventos cumple con los prerequisitos.
        
        Args:
            sequence: Lista de eventos en orden propuesto
            
        Returns:
            Diccionario con resultados de validación
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "missing_prerequisites": {}
        }
        
        processed_events = set()
        
        for i, event in enumerate(sequence):
            if event not in self.events:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Evento {event} no existe")
                continue
                
            event = self.events[event]
            missing_prereqs = []
            
            for prereq in event.prerequisites:
                if prereq not in processed_events:
                    missing_prereqs.append(prereq)
            
            if missing_prereqs:
                validation_result["valid"] = False
                validation_result["missing_prerequisites"][event] = missing_prereqs
            
            processed_events.add(event.title)
        
        return validation_result
    
    # def visualize_graph(self, 
    #                    layout: str = "kamada_kawai",
    #                    figsize: tuple = (12, 8),
    #                    node_size: int = 2000,
    #                    font_size: int = 8):
    #     """
    #     Visualiza el grafo de eventos con diferentes opciones de diseño.
        
    #     Args:
    #         layout: Tipo de layout ('kamada_kawai', 'circular', 'spring', 'shell')
    #         figsize: Tamaño de la figura
    #         node_size: Tamaño de los nodos
    #         font_size: Tamaño de la fuente
    #     """
    #     plt.figure(figsize=figsize)
        
    #     # Seleccionar layout
    #     pos = self._get_layout(layout)
        
    #     # Dibujar nodos y aristas
    #     node_colors = self._get_node_colors()
    #     edge_colors, edge_styles = self._get_edge_attributes()
        
    #     nx.draw_networkx_nodes(self.graph, pos, node_size=node_size, node_color=node_colors)
    #     nx.draw_networkx_labels(self.graph, pos, font_size=font_size)
        
    #     # Dibujar diferentes tipos de aristas
    #     for edge_type in EdgeType:
    #         edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d['type'] == edge_type]
    #         nx.draw_networkx_edges(
    #             self.graph, pos, edgelist=edges,
    #             edge_color=edge_colors[edge_type],
    #             style=edge_styles[edge_type],
    #             arrows=True,
    #             arrowsize=20,
    #             arrowstyle='->',
    #         )
        
    #     # Crear leyenda
    #     self._create_legend(edge_colors, edge_styles)
        
    #     plt.title("Grafo de Eventos de la Historia")
    #     plt.axis("off")
    #     plt.tight_layout()
    #     plt.show()

    # def visualize_graph(self):
    #     # Configura la ruta manualmente
    #     os.environ['PYVIS_TEMPLATE_PATH'] = r"C:\Users\53552\AppData\Local\Programs\Python\Python311\Lib\site-packages\pyvis\templates"
    #     net = Network(directed=True, notebook=False)
    #     net.from_nx(self.graph)
    #     net.show("grafo.html", notebook=False)  # Abre en navegador

    def visualize_graph(self, output_file="grafo.html"):
        """Visualiza el grafo con colores diferenciados por node_type"""
        os.environ['PYVIS_TEMPLATE_PATH'] = r"C:\Users\53552\AppData\Local\Programs\Python\Python311\Lib\site-packages\pyvis\templates"
        net = Network(directed=True, notebook=False)
        
        # Mapeo de colores por tipo de nodo
        node_type_colors = {
            "event": "#FF6B6B",     
            "character": "#4ECDC4",  
            "item": "#FFD166",      
            "location": "#6BFF97",   
            "default": "#A0A0A0"    
        }
        
        # Añadir nodos con atributos de color
        for node, node_attrs in self.graph.nodes(data=True):
            node_type = node_attrs.get("node_type", "default")
            color = node_type_colors.get(node_type, node_type_colors["default"])
            
            net.add_node(
                node,
                label=node,
                color=color,
                title=node_attrs.get("title", ""),
                shape="box" if node_type == "event" else "ellipse"  # Forma diferenciada
            )
        
        # Añadir aristas con colores según tipo de relación
        for edge in self.graph.edges(data=True):
            relation = edge[2].get("relation", "").lower()
            
            # Mapeo de colores por tipo de relación
            relation_colors = {
                "causal": "#FF0000",      
                "temporal": "#00AAFF",   
                "prerrequisito": "#29CC00",
                "appears_in": "#FFA500",  
            }
            
            # Determinar color basado en la relación
            edge_color = relation_colors.get(relation, "#808080")  # Gris por defecto
            
            net.add_edge(
                edge[0], 
                edge[1],
                color=edge_color,
                title=relation,  
                width=2 if relation in relation_colors else 1  # Línea más gruesa para relaciones conocidas
            )
        
        # Configuración de visualización
        net.set_options("""
        {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "springLength": 200
                },
                "minVelocity": 0.75
            },
            "nodes": {
                "font": {
                    "size": 14,
                    "face": "arial"
                }
            }
        }
        """)
        
        net.show(output_file, notebook=False)
    
    def _get_layout(self, layout_name: str) -> Dict:
        """Obtiene la disposición de los nodos según el layout especificado"""
        if layout_name == "kamada_kawai":
            return nx.kamada_kawai_layout(self.graph)
        elif layout_name == "circular":
            return nx.circular_layout(self.graph)
        elif layout_name == "spring":
            return nx.spring_layout(self.graph)
        elif layout_name == "shell":
            return nx.shell_layout(self.graph)
        else:
            return nx.kamada_kawai_layout(self.graph)
    
    def _get_node_colors(self) -> List:
        """Asigna colores a los nodos basados en propiedades"""
        colors = []
        for node in self.graph.nodes():
            # Puedes personalizar esta lógica para diferentes colores
            if len(self.graph.in_edges(node)) == 0:  # Eventos iniciales
                colors.append("lightgreen")
            elif len(self.graph.out_edges(node)) == 0:  # Eventos finales
                colors.append("lightcoral")
            else:
                colors.append("skyblue")
        return colors
    
    def _get_edge_attributes(self) -> tuple:
        """Obtiene colores y estilos para los diferentes tipos de aristas"""
        edge_colors = {
            "temporal": "gray",
            "prerequisite": "red",
            "causal": "green",
            "character": "blue",
            "location": "orange",
            "item": "purple"
        }
        
        edge_styles = {
            "temporal": "dashed",
            "prerequisite": "solid",
            "causal": "solid",
            "character": "dotted",
            "location": "dotted",
            "item": "dotted"
        }
        
        return edge_colors, edge_styles
    
    def _create_legend(self, edge_colors: Dict, edge_styles: Dict):
        """Crea una leyenda para el grafo"""
        from matplotlib.lines import Line2D
        
        legend_elements = [
            Line2D([0], [0], color=edge_colors["prerequisite"], 
                  linestyle=edge_styles["prerequisite"], 
                  label='Prerequisito', lw=2),
            Line2D([0], [0], color=edge_colors["temporal"], 
                  linestyle=edge_styles["temporal"], 
                  label='Temporal', lw=2),
            Line2D([0], [0], color=edge_colors["causal"], 
                  linestyle=edge_styles["causal"], 
                  label='Causal', lw=2),
            Line2D([0], [0], marker='o', color='lightgreen', 
                  label='Evento Inicial', markersize=10, linestyle='None'),
            Line2D([0], [0], marker='o', color='lightcoral', 
                  label='Evento Final', markersize=10, linestyle='None'),
            Line2D([0], [0], marker='o', color='skyblue', 
                  label='Evento Intermedio', markersize=10, linestyle='None')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right')
    
    def to_dict(self) -> Dict:
        """Serializa el grafo de eventos a un diccionario"""
        return {
            "events": [event.to_dict() for event in self.events.values()],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "type": d["type"].name,
                    "label": d.get("label", "")
                }
                for u, v, d in self.graph.edges(data=True)
            ]
        }
