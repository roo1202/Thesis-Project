from collections import deque
import json
import re
from ConversationalAgents.ConversationalAgent import ConversationalAgent
from ConversationalAgents.Gemini import Gemini
from PlotMind.ContextRetrieval import ContextRetrieval
from StoryGraphGenerator.EntityRecognition import EntityRecognition
from StoryGraphGenerator.RelationshipManager import EntityRelationship, RelationshipManager
from StoryGraphGenerator.GraphGenerator import GraphGenerator
from DramaManager.DramaManager import DramaManager
from DependencyManager.DependencyManager import DependencyManager
from StorySpace.Character import Character
from StorySpace.Entity import Entity
from StorySpace.Event import Event
from StorySpace.Item import Item
from StorySpace.Location import Location
from typing import Dict, List
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

    def run(self, inicial_description: str):
        """
        Ejecuta el generador interactivo de tramas
        """
        start = True
        print("Bienvenido a PlotMind, el generador interactivo de tramas.")
        print("Escribe 'salir' para terminar la sesión.")
        if start:
            user_input = inicial_description
            
            prompt = f"""
            Extract:
            {{
                "narrative_structure": estructura narrativa,
                "gender": género (ej: fantasía, ciencia ficción),
                "extension":(int) Número de pasajes de la historia (puedes inferirlo si se menciona la extensión que se quiere),
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

            data = self.model.clean_answer(resp)
            
            self.narrative_structure = data.get("narrative_structure", "Estructura básica")
            self.gender = data.get("gender", "Género no especificado")
            if data.get("extension") is None:
                self.extension = ""
            else:
                e = str(data.get("extension")).isdigit()
                self.extension = max(int(data.get("extension")), 5)
            self.style = data.get("style", "Tono informal sin exceso de adjetivación")
            self.rules = data.get("rules", [])
            
        else:
            user_input = input("Escribe algo más sobre tu historia: ")
        

        extraction = self.recognizer.extract_entities(user_input, [Location, Character, Item, Event])

        rm : List[str] = []
        e_rm : List[str] = []
        events_meta = []
    
        for entity in extraction:
            if entity == "personajes":
                if isinstance(extraction[entity],list):
                    for character in extraction[entity]:
                        rm.append(character["name"])
                        if character["name"] in self.characters.keys():
                            self.characters[character["name"]].add_features(character)
                        else:
                            self.characters[character["name"]] = Character(**character)
                elif isinstance(extraction[entity],dict):
                    for character in extraction[entity].values():
                        rm.append(character["name"])
                        if character["name"] in self.characters.keys():
                            self.characters[character["name"]].add_features(character)
                        else:
                            self.characters[character["name"]] = Character(**character)
            elif entity == "eventos":
                if isinstance(extraction[entity],list):
                    for event in extraction[entity]:
                        e_rm.append(event['title'])
                        events_meta.append(event)
                        if event['title'] in self.graph.events.keys():
                            self.graph.events[event["title"]].add_features(event)
                        else:
                            self.graph.add_event(event= Event(**event))
                elif isinstance(extraction[entity],dict):
                    for event in extraction[entity].values():
                        e_rm.append(event['title'])
                        events_meta.append(event)
                        if event['title'] in self.graph.events.keys():
                            self.graph.events[event["title"]].add_features(event)
                        else:
                            self.graph.add_event(event= Event(**event))
            elif entity == "ubicaciones":
                if isinstance(extraction[entity],list):
                    for location in extraction[entity]:
                        rm.append(location["name"])
                        if location["name"] in self.locations.keys():
                            self.locations[location["name"]].add_features(location)
                        else:
                            self.locations[location["name"]] = Location(**location)
                elif isinstance(extraction[entity], dict):
                    for location in extraction[entity].values():
                        rm.append(location["name"])
                        if location["name"] in self.locations.keys():
                            self.locations[location["name"]].add_features(location)
                        else:
                            self.locations[location["name"]] = Location(**location)
            elif entity == "ítems":
                if isinstance(extraction[entity],list):
                    for item in extraction[entity]:
                        rm.append(item["name"])
                        if item["name"] in self.items.keys():
                            self.items[item["name"]].add_features(item)
                        else:
                            self.items[item["name"]] = Item(**item)
                elif isinstance(extraction[entity],dict):
                    for item in extraction[entity].values():
                        rm.append(item["name"])
                        if item["name"] in self.items.keys():
                            self.items[item["name"]].add_features(item)
                        else:
                            self.items[item["name"]] = Item(**item)

        self.graph = GraphGenerator()

        while isinstance(self.extension, int) and self.extension > 0:
            extension = min(self.extension, 20)
            self.extension -= 20

            prompt = f"""
            Genera {extension} eventos narrativos coherentemente que sigan como estructura narrativa {self.narrative_structure}, con género {self.gender}, con tono {self.style}.
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
            resp = self.model.ask(prompt, temperature=0.9)
            data = self.model.clean_answer(resp)
            suggested_events = data.get("eventos_sugeridos", [])
            text = ""

            for e in suggested_events:
                self.graph.add_event(Event(**e) )
                
        for e in self.graph.events.values():
            text += (e.description)
            print(e.description)
            print("\n")


        # Mejorando el mundo de la historia según los eventos sugeridos

        characters_data = self.model.clean_answer(self.dramaManager.impove_characters([character for character in self.characters.values()], text))
        if isinstance(characters_data, dict):
            new_characters = characters_data.get("personajes", [])
        else:
            new_characters = characters_data

        for character in new_characters:
            self.characters[character["name"]] = Character(**character)

        # print("Nuevos personajes::", json.dumps(new_characters, indent=2, ensure_ascii=False))

        locations_data = self.model.clean_answer(self.dramaManager.impove_locations([location for location in self.locations.values()], text))
        if isinstance(locations_data, dict):
            new_locations = locations_data.get("ubicaciones", [])
        else:
            new_locations = locations_data

        for location in new_locations:
            self.locations[location["name"]] = Location(**location)

        # print("Nuevas ubicaciones:", json.dumps(new_locations, indent=2, ensure_ascii=False))

        items_data = self.model.clean_answer(self.dramaManager.impove_items([item for item in self.items.values()], text))
        if isinstance(items_data, dict):
            new_items = items_data.get("items", [])
        else:
            new_items = items_data

        for item in new_items:
            self.items[item["name"]] = Item(**item)

        # print("Nuevos ítems:", json.dumps(new_items, indent=2, ensure_ascii=False))
        
        # Relacionar entidades y eventos
        self.update_entities_in_events(events=[e for e in self.graph.events.values()], entities=[character for character in self.characters.values()] + [location for location in self.locations.values()] + [item for item in self.items.values()])

        entities = [character for character in self.characters.keys()] + [location for location in self.locations.keys()] + [item for item in self.items.keys()]

        print("Extrayendo relaciones...")
        relations = self.relationshipsManager.infer_relationships_from_text(entities, list(self.graph.events.values()))

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
            cycles = list(nx.simple_cycles(self.graph.graph))
            print("Los ciclos encontrados son:")
            for cycle in cycles:
                print(f"Ciclo: {cycle}")

        
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

        for clus,info in clustering_result['cluster_details'].items():
            print(f"Cluster {clus} tiene {info['size']} eventos.")
            print(f"Eventos en el cluster: {info['sample_titles']}")

        if len(clustering_result) > 100:
            # Crear mapeo de nodo a cluster_id
            node_to_cluster = {
                node: clustering_result['labels'][i] 
                for i, node in enumerate(self.graph.graph.nodes)
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

        for relation in relations:
            if isinstance(relation, EntityRelationship):
                self.graph.add_entities_relation(relation)

        # Visualizar el grafo
        print("\nVisualizando grafo de eventos...")
        self.graph.visualize_graph()


        # Generar el texto narrativo 
        plot=list(self.graph.events.values())
        characters_introduced = {character.name : False for character in self.characters.values()}
        locations_introduced = {location.name : False for location in self.locations.values()}
        items_introduced = {item.name : False for item in self.items.values()}
        events_introduced = {event.title : False for event in self.graph.events.values()}
        window = deque(maxlen=3) 

        prompt = f"""
            Eres un narrador experto de historias. Tu misión es generar un texto narrativo que describa el siguiente evento con el que comienza la historia.
            El evento se titula {plot[0].title}, se desarrolla en {plot[0].locations[0]} y se describe como: {plot[0].description}
            Puedes introducir las ubicaciones, personajes e items haciendo breves descripciones de ellos ya que se presentan por primera vez, según consideres para no cargar el texto.
            Las ubicaciones son: {[location.to_dict() for location in self.locations.values() if location.name in plot[0].locations]}
            Los personajes son: {[character.describe_character_with_event(plot[0].title) for character in self.characters.values() if character.name in plot[0].characters_involved]}
            Los items son: {[item.to_dict() for item in self.items.values() if item.name in plot[0].items_involved]}
            La narración sigue la estructura narrativa {self.narrative_structure}, este evento pertenece a {plot[0].narrative_part}, tenlo en cuenta para la longitud del texto generado.
        """
        
        if self.gender is not None:
            prompt += f"El género de la historia es {self.gender}."
        if self.style is not None:
            prompt += f"El estilo de la historia es {self.style}."
        # if len(self.rules) > 0:
        #     prompt += f"Ten en cuenta los siguientes deseos del autor: {', '.join(self.rules)}."
        prompt += "Devuelve solo el texto narrativo como se presentaría al lector, sin comentarios adicionales y en español."

        # Marcar los personajes, ubicaciones e items introducidos en el texto
        for c in plot[0].characters_involved:
            if c in characters_introduced:
                characters_introduced[c] = True
                self.characters[c].current_location = plot[0].locations[0]  # Actualizar ubicación actual del personaje
        for l in plot[0].locations:
            if l in locations_introduced:
                locations_introduced[l] = True
        for i in plot[0].items_involved:
            if i in items_introduced:
                items_introduced[i] = True

        events_introduced[plot[0].title] = True
        # print(prompt)
        plot[0].description = self.model.ask(prompt)
        window.append(plot[0])
      
        for event in plot[1:-1]:
            window.append(event)
            context = self.context_retriever.get_context([e.title for e in window])
            prompt = f"""
                Eres un narrador experto de historias. Tu misión es generar un texto narrativo coherente para el siguiente evento.
                Devuelve solo el texto narrativo de este evento, como se presentaría al lector, sin comentarios adicionales y en español.
                El evento se titula {event.title}, se desarrolla en {event.locations[0] if len(event.locations)>0 else "lugar desconocido"} y se describe como: {event.description}
                Redacta el texto de manera que sea coherente con el texto de los eventos anteriores, pero no los repitas, genera texto solo para este evento.
                El texto de los eventos anteriores es:
                {", ".join([f"{e.description}" for e in list(window)[:-1]])}
            """

            locations_to_present = [location.to_dict() for location in self.locations.values() if (location.name in event.locations and not locations_introduced[location.name])]
            characters_to_present = [character.describe_character_with_event(event.title) for character in self.characters.values() if (character.name in event.characters_involved and not characters_introduced[character.name])]
            items_to_present = [item.to_dict() for item in self.items.values() if (item.name in event.items_involved and not items_introduced[item.name])]

            if len(locations_to_present) > 0 or len(characters_to_present) > 0 or len(items_to_present) > 0:
                prompt += f"Puedes introducir las siguientes ubicaciones, personajes e items haciendo breves descripciones de ellos ya que se presentan por primera vez, según consideres para no cargar el texto.\n"
                if len(locations_to_present) > 0:
                    prompt += f"Las ubicaciones son: {locations_to_present}.\n"
                if len(characters_to_present) > 0:
                    prompt += f"Los personajes son: {characters_to_present}.\n"
                if len(items_to_present) > 0:
                    prompt += f"Los items son: {items_to_present}.\n"

            characters_presented = [(character.name, character.current_location) for character in self.characters.values() if (character.name in event.characters_involved and characters_introduced[character.name])]
            if len(characters_presented) > 0:
                prompt += f"Los personajes ya presentados en la historia que intervienen en este evento son: {', '.join([f' {self.characters[name].describe_character_with_event(event.title)} anteriormente estaba en {location}' for name, location in characters_presented])}.\n"

            # Eventos relacionados con el actual que ya se han escrito
            past_context = [c for c in context if events_introduced[c['metadata']['title']]]

            if len(past_context) > 0:
                prompt += f"Eventos pasados de la historia relacionados semánticamente con el evento actual (no mencionar directamente): {', '.join([c['text'] for c in past_context])}.\n"

            # Eventos que aún no se han introducido en la historia
            future_context = [c for c in context if not events_introduced[c['metadata']['title']]]

            if len(future_context) > 0:
                prompt += f"Eventos que van a ocurrir en el futuro relacionados semánticamente con el evento actual (no mencionar directamente): {', '.join([c['text'] for c in future_context])}.\n"


            prompt += f"La narración sigue la estructura narrativa {self.narrative_structure}, este evento pertenece a {event.narrative_part}, tenlo en cuenta para la longitud del texto generado."
            if self.gender is not None:
                prompt += f"El género de la historia es {self.gender}."
            if self.style is not None:
                prompt += f"El estilo de la historia es {self.style}."
            # if len(self.rules) > 0:
            #     prompt += f"Ten en cuenta los siguientes deseos del autor: {', '.join(self.rules)}."
            

            # Marcar los personajes, ubicaciones e items introducidos en el texto
            for c in event.characters_involved:
                if c in characters_introduced:
                    characters_introduced[c] = True
                    self.characters[c].current_location = event.locations[0] if len(event.locations) else "Desconocida" # Actualizar ubicación actual del personaje
            for l in event.locations:
                if l in locations_introduced:
                    locations_introduced[l] = True
            for i in event.items_involved:
                if i in items_introduced:
                    items_introduced[i] = True
            events_introduced[event.title] = True

            # print(prompt)
            event.description = self.model.ask(prompt)
            
        # Añadir el último evento
        last_event = plot[-1]
        window.append(last_event)
        context = self.context_retriever.get_context([e.title for e in window])

        characters_presented = [character.describe_character_with_event(last_event.title) for character in self.characters.values() if character.name in last_event.characters_involved]

        prompt = f"""
            Eres un narrador experto de historias. Tu misión es generar un texto narrativo coherente para el último evento de una historia.
            Devuelve solo el texto narrativo de este evento y que dará fin a la historia, como se presentaría al lector, sin comentarios adicionales y en español.
            El evento se titula {last_event.title}, se desarrolla en {last_event.locations[0]} y se describe como: {last_event.description}
            Redacta el texto de manera que sea coherente con el texto de los eventos anteriores, pero no los repitas, genera texto solo para este evento.
            El texto de los eventos anteriores es:
            {", ".join([f"{e.description}" for e in list(window)[:-1]])}
            Las ubicaciones, personajes e items que aparecen en el evento se describen a continuación.
            Las ubicaciones son: {[location.to_dict() for location in self.locations.values() if location.name in last_event.locations]}
            Los personajes son: {[characters_presented[i] + "Anteriormente estaba en " + self.characters[character].current_location for i, character in enumerate(last_event.characters_involved)]}
            Los items son: {[item.to_dict() for item in self.items.values() if item.name in last_event.items_involved]}
            La narración sigue la estructura narrativa {self.narrative_structure}, este evento pertenece a {last_event.narrative_part}, tenlo en cuenta en la longitud del texto generado.
        """
        prompt += f"A continuacion se describen eventos anteriores que pueden ser relevantes para el contexto de este evento: {', '.join([c['text'] for c in context])}.\n"

        if self.gender is not None:
            prompt += f"El género de la historia es {self.gender}."
        if self.style is not None:
            prompt += f"El estilo de la historia es {self.style}."
        # if len(self.rules) > 0:
        #     prompt += f"Ten en cuenta los siguientes deseos del autor: {', '.join(self.rules)}."

        # print(prompt)
        plot[-1].description = self.model.ask(prompt)	

        # Guardar la historia en un archivo de texto
        story = ("\n\n").join([e.description for e in plot])	
        story = self.editar_texto_largo(story)

        with open("stories.txt", "a", encoding="utf-8") as archivo:
            archivo.write("\n Prompt inicial: " + inicial_description + "\n\n")

        with open("stories.txt", "a", encoding="utf-8") as archivo:
            archivo.write(story)

        return story



    def update_entities_in_events(self, events: List[Event], entities: List[Entity]) -> None:
        """
        Actualiza las entidades en cada evento del mundo de la historia.
        """
        print("Actualizando entidades...")
        # Relacionar entidades y eventos
        entities_in_events = self.recognizer.identify_entities(events,entities)

        entities_in_events = self.model.clean_answer(entities_in_events)
        entities_in_events = entities_in_events.get("events", [])
        self.graph = GraphGenerator()
        for e in entities_in_events:
            self.graph.add_event(event=Event(**e) )
            print(e)
            print("\n")
        return
    
    def editar_texto_largo(self, texto: str, palabras_por_chunk: int = 500) -> str:
        """
        Edita un texto largo dividiéndolo en chunks y procesando cada uno con el modelo.
        
        Args:
            texto: Texto completo a editar
            palabras_por_chunk: Número de palabras por segmento (ajustar según límites del modelo)
            
        Returns:
            Texto editado y unificado
        """
        # Dividir el texto en palabras
        palabras = texto.split()
        texto_editado = []
        
        # Procesar por chunks
        for i in range(0, len(palabras), palabras_por_chunk):
            chunk = ' '.join(palabras[i:i+palabras_por_chunk])
            
            # Crear el prompt de edición
            prompt = (
                "Eres un editor literario profesional. Tu tarea es editar el siguiente texto:\n"
                "1. Eliminar repeticiones y descripciones innecesarias\n"
                "2. Quitar redundancias\n"
                "3. Eliminar mayúsculas si no son nombres propios o comienzos de oración\n"
                "4. Conservar el estilo y significado original\n"
                "5. NO añadir comentarios ni texto adicional\n\n"
                f"Texto a editar:\n{chunk}\n\n"
                "Texto editado:"
            )
            
            # Obtener respuesta del modelo
            try:
                respuesta = self.model.ask(prompt)
                
                # Verificar que la respuesta sea válida
                if respuesta and isinstance(respuesta, str) and len(respuesta) > 0:
                    texto_editado.append(respuesta.strip())
                    
            except Exception as e:
                print(f"Error procesando chunk {i//palabras_por_chunk}: {e}")

        # Unir todos los chunks editados
        return ' '.join(texto_editado)
        
            