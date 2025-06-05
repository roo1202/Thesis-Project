import re
import time
from ConversationalAgents.ConversationalAgent import ConversationalAgent
from ConversationalAgents.Gemini import Gemini
from PlotMind.ContextRetrieval import ContextRetrieval
from StoryGraphGenerator.EntityRecognition import EntityRecognition
from StoryGraphGenerator.RelationshipManager import RelationshipManager
from StoryGraphGenerator.GraphGenerator import GraphGenerator
from DramaManager.DramaManager import DramaManager
from DependencyManager.DependencyManager import DependencyManager
from StorySpace.Character import Character
from StorySpace.Entity import Entity
from StorySpace.Event import Event
from StorySpace.Item import Item
from StorySpace.Location import Location
from typing import Dict, List
import json
import networkx as nx


class PlotMind:
    def __init__(self, model : ConversationalAgent = Gemini()):
        """Inicializa la clase PlotMind"""
        self.model = model
        self.recognizer = EntityRecognition(model)
        self.relationshipsManager = RelationshipManager(model)
        self.graph = GraphGenerator()
        self.context_retriever = ContextRetrieval()
        self.dramaManager = DramaManager(model)
        self.characters : Dict[str, Character] = {}
        self.locations : Dict[str, Location] = {}
        self.items : Dict[str, Item] = {}
        self.narrative_structure : str = "estructura básica"
        self.gender :str = ""
        self.extension = None
        self.style :str = ""
        self.rules : List[str] = []

    def run(self):
        """
        Ejecuta el generador interactivo de tramas
        """
        start = True
        print("Bienvenido a PlotMind, el generador interactivo de tramas.")
        print("Escribe 'salir' para terminar la sesión.")
        if start:
            user_input = input("""
                Comencemos a crear tu historia. 
                Ingrese algunos parámetros iniciales para la historia (opcionales):
                    1. Estructura narrativa: ¿Tienes alguna estructura narrativa en mente?
                    2. Género: ¿Qué tipo de historia quieres contar? (ej: fantasía, ciencia ficción, etc.)
                    3. Extensión: ¿Cuántos párrafos o pasajes quieres que tenga la historia?
                    4. Tono y estilo: ¿Qué tono deseas? (ej: serio, humorístico, poético)
                    5. Reglas en particular que se deben cumplir en la historia 
                En caso de no tener ningún parámetro predefinido, presione 'enter' para continuar: 
            """)	
            
            prompt = f"""
            Extract:
            {{
                "narrative_structure": estructura narrativa,
                "gender": género (ej: fantasía, ciencia ficción),
                "extension":(int) Número de párrafos o pasajes de la historia,
                "style": tono y estilo (ej: serio, humorístico, poético)
                "rules": lista de reglas que el autor quiere que cumpla la historia
            }}
            If not specified, infer it from the text provided.
            From the following text:
            {user_input}
            In valid JSON format. 
            """
            #print(prompt)
            resp = self.model.ask(prompt)

            data = clean_answer(resp)
            
            self.narrative_structure = data.get("narrative_structure", "Estructura básica")
            self.gender = data.get("gender", "Género no especificado")
            self.extension = int(data.get("extension", "15"))
            self.style = data.get("style", "Tono y estilo no especificado")
            self.rules = data.get("rules", [])
            
            user_input = input("""
                Para ayudarte a desarrollar una narrativa sólida, necesito que me compartas todo lo que puedas sobre el proyecto que tienes en mente. 
                No importa si son ideas sueltas o detalles muy específicos: cada pieza es valiosa.
                Puedes incluir:
                Personajes principales: Nombres, roles, personalidades, motivaciones.
                Mundo narrativo: ¿Es realista, mágico, futurista? ¿Hay reglas especiales (ej: magia, tecnología)?
                Conflicto central: ¿Qué problema impulsa la historia? (ej: una guerra, un misterio, un viaje).
                Extras: Escenas clave que ya imaginas, temas que quieres explorar (ej: redención, identidad), o preguntas sin resolver.
                            
                No te preocupes por el orden o la coherencia en esta etapa. 
                ¡Aquí lo importante es capturar tu visión! Una vez que me compartas estos detalles, 
                trabajaremos juntos para darle forma.
            """)
        else:
            user_input = input("Escribe algo más sobre tu historia: ")
        

        extraction = self.recognizer.extract_entities(user_input, [Location, Character, Item, Event])

        rm : List[str] = []
        e_rm : List[str] = []
        events_meta = []
    
        for entity in extraction:
            if entity == "personajes":
                for character in extraction[entity]:
                    rm.append(character["name"])
                    if character["name"] in self.characters.keys():
                        self.characters[character["name"]].add_features(character)
                    else:
                        self.characters[character["name"]] = Character(**character)
            elif entity == "eventos":
                for event in extraction[entity]:
                    e_rm.append(event['title'])
                    events_meta.append(event)
                    if event['title'] in self.graph.events.keys():
                        self.graph.events[event["title"]].add_features(event)
                    else:
                        self.graph.add_event(event= Event(**event))
            elif entity == "ubicaciones":
                for location in extraction[entity]:
                    rm.append(location["name"])
                    if location["name"] in self.locations.keys():
                        self.locations[location["name"]].add_features(location)
                    else:
                        self.locations[location["name"]] = Location(**location)
            elif entity == "ítems":
                for item in extraction[entity]:
                    rm.append(item["name"])
                    if item["name"] in self.items.keys():
                        self.items[item["name"]].add_features(item)
                    else:
                        self.items[item["name"]] = Item(**item)

        prompt = f"""
        Genera {self.extension} eventos narrativos coherentemente que sigan como estructura narrativa {self.narrative_structure}, con género {self.gender}, con tono {self.style}.
        La salida debe ser de la siguiente forma:
        {{
            "eventos_sugeridos": [  
                {{  
                    title: Título del evento
                    description: Descripción del evento sin muchos detalles
                    narrative_part: parte de la estructura narrativa en la que se ubicaría el evento
                }}  
            ]
        }}
        Incluye los siguientes eventos:
        {     " - ".join([f"{event.description}" for event in self.graph.events.values()]) }
        Ten en cuenta las siguientes reglas:
        {", ".join(self.rules)}
        Ten en cuenta los siguientes personajes:
        {", ".join([f"{character.description_summary()}" for character in self.characters.values()]) }
        Ten en cuenta los siguientes lugares:
        {", ".join([f"{location.description_summary()}" for location in self.locations.values()]) }
        Ten en cuenta los siguientes items:
        {", ".join([f"{item.description_summary()}" for item in self.items.values()]) }
        """

        print(prompt)
        resp = self.model.ask(prompt)
        data = clean_answer(resp)
        suggested_events = data.get("eventos_sugeridos", [])
        text = ""
        last_event = False

        self.graph = GraphGenerator()

        for e in suggested_events:
            self.graph.add_event(Event(**e) )
            if last_event:
                self.graph.add_temporal_relation(last_event, e["title"])
            last_event = e["title"]
            text += (e["description"])
            print(e)
            print("\n")


        # Mejorando el mundo de la historia según los eventos sugeridos

        characters_data = clean_answer(self.dramaManager.impove_characters([character for character in self.characters.values()], text))
        new_characters = characters_data.get("personajes", [])

        for character in new_characters:
            self.characters[character["name"]] = Character(**character)

        # print("Nuevos personajes::", json.dumps(new_characters, indent=2, ensure_ascii=False))

        locations_data = clean_answer(self.dramaManager.impove_locations([location for location in self.locations.values()], text))
        new_locations = locations_data.get("ubicaciones", [])

        for location in new_locations:
            self.locations[location["name"]] = Location(**location)

        # print("Nuevas ubicaciones:", json.dumps(new_locations, indent=2, ensure_ascii=False))

        items_data = clean_answer(self.dramaManager.impove_items([item for item in self.items.values()], text))
        new_items = items_data.get("items", [])

        for item in new_items:
            self.items[item["name"]] = Item(**item)

        # print("Nuevos ítems:", json.dumps(new_items, indent=2, ensure_ascii=False))
        
        # Relacionar entidades y eventos
        self.update_entities_in_events(events=[e for e in self.graph.events.values()], entities=[character for character in self.characters.values()] + [location for location in self.locations.values()] + [item for item in self.items.values()])

        entities = [character for character in self.characters.keys()] + [location for location in self.locations.keys()] + [item for item in self.items.keys()]
        events = []
        text = ""
        for name,event in self.graph.events.items():
            events.append(name)
            text += event.description

        print("Extrayendo relaciones...")
        relations = self.relationshipsManager.infer_relationships_from_text(text, entities, events)

        # Añadir relaciones al grafo
        for relation in relations:
            if relation.relationship_type == 'causal':
                self.graph.add_causal_relation(relation.entity1, relation.entity2)
            elif relation.relationship_type == 'prereq':
                self.graph.add_prereq_relation(relation.entity1, relation.entity2)
                self.graph.events[relation.entity2].prerequisites.append(relation.entity1)


        # # Visualizar el grafo
        # print("\nVisualizando grafo de eventos...")
        # self.graph.visualize_graph()

        # Simulando el personaje sobre toda la historia
        # for name,character in self.characters.items():
        #     print(f"Personaje {name}:")
        #     events_involved = []
        #     for event in self.graph.events.values():
        #         if name in event.characters_involved:
        #             events_involved.append(event)
        #     self.characters[name] = self.dramaManager.simulate_character(character, events_involved)
        #     time.sleep(3)
        #     print("Acciones :")
        #     print(self.characters[name].actions)
        #     print("Motivaciones :")
        #     print(self.characters[name].motivations)
        #     print("Metas :")
        #     print(self.characters[name].goals)


        # Simulando cada paso de la historia con todos los personajes
        for event in self.graph.events.values():
            updated_characters = self.dramaManager.simulate_event(event, [character for name,character in self.characters.items() if name in event.characters_involved])
            for character in updated_characters:
                self.characters[character.name]= character
            time.sleep(5)
        
        # Comprobando acciones de los personajes y tomando sugerencias para enriquecer la historia
        suggested_events_for_the_characters = []
        for character in self.characters.values():
            c,e = self.dramaManager.check_character_actions(character)
            self.characters[character.name] = c
            suggested_events_for_the_characters.extend(e)

        #print(suggested_events_for_the_characters)

        # Seleccionando de los eventos sugeridos los que aporten a la trama sin desviarla
        events_to_add = self.dramaManager.select_significant_events(suggested_events_for_the_characters, text, self.rules)

        #print("Eventos escogidos:")
        for e in events_to_add:
            #print(e.to_dict())
            self.graph.add_event(e)

        # Añadiendo elementos literarios a los eventos existentes
        new_events = self.dramaManager.add_literary_elements([event for event in self.graph.events.values()], self.gender, self.style)
        for e in new_events:
            self.graph.events[e.title] = e
            #print(f"Evento mejorado: {e.description}")


        # Comprobar dependencias y relaciones entre el mundo de la historia y los eventos
        if not DependencyManager.is_multidigraph_dag(self.graph.graph):
            print("El grafo de eventos contiene ciclos o no es un DAG. No se pueden generar más eventos.")
            # Revisar las relaciones entre los eventos

        # Crear relaciones entre los personajes y los eventos en el grafo
        for c in self.characters.values():
            if len(c.actions) > 0:
                self.graph.add_character(c)
                self.graph.link_character_to_events(c.name, c.actions)

        # Crear relaciones entre los items y los eventos en el grafo
        for item in self.items.values():
            self.graph.add_item(item)
            for event in self.graph.events.values():
                if item.name in event.items_involved:
                    self.graph.link_item_to_event(item.name, event.title)

        # Visualizar el grafo
        print("\nVisualizando grafo de eventos...")
        self.graph.visualize_graph()

        
        # Generar embeddings de texto para los eventos
        self.context_retriever.add_events(list(self.graph.events.values()))

        # Detección de subtramas mediante clustering semántico y componentes conexas de eventos
        # 1. Obtener subgrafos de eventos conectados
        subgraphs = [self.graph.graph.subgraph(c) for c in nx.weakly_connected_components(self.graph.graph)]

        # 2. Filtrar subgrafos por coherencia temática
        valid_subplots = []
        clustering_result = self.context_retriever.get_clusters(
            min_samples=3 if self.extension < 50 else 5
        )

        # Crear mapeo de nodo a cluster_id
        node_to_cluster = {
            node: clustering_result['labels'][i] 
            for i, node in enumerate(self.graph.graph.nodes())
        }

        for sg in subgraphs:
            # Obtener clusters únicos de los nodos en este subgrafo
            cluster_ids = {node_to_cluster[node] for node in sg.nodes}
            
            # Considerar válido si:
            # 1. Todos están en el mismo cluster (excluyendo ruido -1), o
            # 2. Hay un solo cluster_id no-ruido y el resto son ruido (-1)
            non_noise_clusters = {cid for cid in cluster_ids if cid != -1}
            
            if len(non_noise_clusters) == 1:
                valid_subplots.append(sg)
            
        for subplot in valid_subplots:
            events_description = []
            for node in subplot.nodes:
                event = self.graph.events.get(node, None)
                if event:
                    events_description.append(event.description)
            print(self.relationshipsManager.verify_subplot(events_description))
                    

        return





        last_events = self.graph.get_last_events(3)
        characters_involved = []
        places_involved = []
        items_involved = []

        for e in last_events:
            characters_involved.extend([c for c in self.graph.events[e].characters_involved if c not in characters_involved])
            places_involved.extend([p for p in self.graph.events[e].locations if p not in places_involved])
            items_involved.extend([i for i in self.graph.events[e].items_involved if i not in items_involved])

        history_events = self.context_retriever.get_context(last_events, k=3, m=3)

        # print("Eventos recientes:")
        # print(last_events)

        # print("Personajes involucrados:")
        # print(characters_involved)

        # print("Lugares involucrados:")
        # print(places_involved)

        # print("Items involucrados:")
        # print(items_involved)

        # print("Eventos históricos relevantes:")
        # print(history_events)

        prompt = f"""
            Eres un narrador experto en historias interactivas. Tu misión es generar eventos narrativos coherentes basados en:
            -El estado actual del mundo (eventos recientes, personajes, lugares, items).
            -El contexto histórico (eventos pasados relevantes).
            -La estructura narrativa definida, el género y el estilo, los eventos restantes para concluir la historia.
            -Reglas que debes tener en cuenta para generar los eventos.
            Información de la historia:
            {{ 
                "mundo_actual": {{ 
                    "eventos": {[self.graph.events[event].to_dict() for event in last_events if event in self.graph.events]},
                    "personajes": {[self.characters[character].to_dict() for character in characters_involved if character in self.characters]},
                    "lugares": {[self.locations[place].to_dict() for place in places_involved if place in self.locations]},
                    "items": {[self.items[item].to_dict() for item in items_involved if item in self.items]}
                }},  
                "contexto_histórico": {{  
                    "eventos_pasados": {[self.graph.events[event_data["text"]].to_dict() for event_data in history_events if event_data["text"] in self.graph.events]}
                }},  
                "estructura": {{  
                    "tipo": {self.narrative_structure},
                    "género": {self.gender},
                    "style": {self.style},
                    "eventos_restantes": {self.extension}
                }},
                "reglas": {[rule for rule in self.rules]}
            }}
            Analiza el contexto histórico y el estado actual del mundo de la historia.
            Genera 3 eventos que den continuidad a la historia, que:
            -Sean lógicos dado el estado actual de la historia.
            -Avancen la trama según los eventos restantes y encajen en la estructura narrativa.
            -Respeten las reglas definidas.
            Devuelve solo un JSON válido, sin comentarios adicionales con los posibles eventos, de la siguiente forma: 
            {{  
                "eventos_sugeridos": [  
                    {{  
                        title: Título del evento
                        description: Descripción detallada del evento, con elementos narrativos
                        prerequisites: Lista de eventos que deben ocurrir antes de este evento
                        effects: Cambios que produce este evento
                    }}  
                ]
            }}
        """

        # print("Prompt que se proporciona como contexto:")
        # print(prompt)

        resp = self.model.ask(prompt)

        data = clean_answer(resp)

        suggested_events = data.get("eventos_sugeridos", [])

        user_input = ""
        for e in suggested_events:
            self.graph.add_event(Event(**e) )
            print(e)
            print("\n")
            user_input += e["description"] + "\n"

        next_step = input("¿Quieres continuar con la historia? (s/n): ")

        self.extension -= len(suggested_events)

        for title,event in self.graph.events.items():
            print(title)
            print(event.description)
            print("\n")


    def update_entities_in_events(self, events: List[Event], entities: List[Entity]) -> None:
        """
        Actualiza las entidades en cada evento del mundo de la historia.
        """
        print("Actualizando entidades...")
        # Relacionar entidades y eventos
        entities_in_events = self.recognizer.identify_entities(events,entities)

        entities_in_events = clean_answer(entities_in_events)
        entities_in_events = entities_in_events.get("events", [])
        self.graph = GraphGenerator()
        for e in entities_in_events:
            self.graph.add_event(event=Event(**e) )
            print(e)
            print("\n")
        return
    
            

def clean_answer(answer: str) -> Dict:
    """
    Limpia la respuesta del modelo para eliminar caracteres innecesarios.
    Args:
        answer: Respuesta cruda del modelo.
    Returns:
        Respuesta limpia.
    """
    # try:
    #     # Limpiar la respuesta
    #     clean_response = (answer).strip()
    #     if clean_response.startswith("```json"):
    #         clean_response = clean_response[7:]
    #     if clean_response.endswith("```"):
    #         clean_response = clean_response[:-3]
            
    #     # Parsear JSON
    #     return json.loads(clean_response)
    # except (json.JSONDecodeError, KeyError) as e:
    #     print(f"Error limpiando respuesta: {e}")
    #     print(f"Respuesta recibida: {answer}")
    #     return {}
    try:
        # Limpieza robusta (incluye casos con '```json' y '```' en líneas separadas)
        clean_response = re.sub(r'^```json|```$', '', answer.strip(), flags=re.DOTALL).strip()
        
        # Parsear y validar
        parsed = json.loads(clean_response)
        return parsed
    except json.JSONDecodeError as e:
        print(f"Error de JSON (posible respuesta corrupta): {e}")
        print(f"Contenido problemático (50 chars alrededor del error):")
        error_pos = e.pos
        print(clean_response[max(0, error_pos-25):error_pos+25])  # Contexto del error
        return {}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {}