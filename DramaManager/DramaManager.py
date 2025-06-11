from collections import deque
import time
from typing import Dict, List
from ConversationalAgents.ConversationalAgent import ConversationalAgent
from StorySpace.Character import Character
from StorySpace.Event import Event
from StorySpace.Item import Item
from StorySpace.Location import Location

class DramaManager:
    def __init__(self, model: ConversationalAgent):
        self.model = model
        

    def impove_characters(self, characters :List[Character], story: str)-> str:
        try:
            prompt = f"""
                Let's enrich the world of the story by bringing the characters to life!
                Generates:
                {{
                    personajes : {{[
                    {Character._prompt},]
                    }}
                }}
                In valid JSON format.
                Considering these are the current characters, add others that are mentioned in the story and have not been defined, and improve the existing ones:
                Current characters:
                {[character.to_dict() for character in characters]}
                Story to analize:
                {story}
            """
            resp = self.model.ask(prompt, temperature=0.8)
            return resp
        except Exception as e:
            print(f"Error al mejorar los personajes: {e}")
            time.sleep(5)
        return self.impove_characters(characters, story)
    

    def impove_locations(self, locations :List[Location], story: str)-> str:
        try:
            prompt = f"""
                Let's enrich the world of history by defining the scenarios!
                Generates:
                {{
                    ubicaciones : {{[
                    {Location._prompt},]
                    }}
                }}
                In valid JSON format.
                Considering these are the current locations, add others that are mentioned in the story and have not been defined and improve the existing ones:
                Current locations:
                {[location.to_dict() for location in locations]}
                Story to analize:
                {story}
            """
            resp = self.model.ask(prompt, temperature=0.8)
            return resp
        except Exception as e:
            print(f"Error al mejorar los ubicaciones: {e}")
            time.sleep(5)
        return self.impove_locations(locations, story)
    

    def impove_items(self, items :List[Item], story: str)-> str:
        try:
            prompt = f"""
                Let's enrich the world of history by better defining the important objects in it!
                Generates:
                {{
                    items : {{[
                    {Item._prompt},]
                    }}
                }}
                In valid JSON format.
                Considering these are the current items, add others that are mentioned in the story and have not been defined and improve the existing ones:
                Current items:
                {[item.to_dict() for item in items]}
                Story to analize:
                {story}
            """
            resp = self.model.ask(prompt, temperature=0.8)
            return resp
        except Exception as e:
            print(f"Error al mejorar los items: {e}")
            time.sleep(5)
        return self.impove_items(items, story)
    

    def simulate_character(self, character: Character, events: List[Event]) -> Character:
        """
        Simula las acciones de un personaje en base a los eventos dados.
        
        Args:
            character: Instancia de la clase Character que representa al personaje
            events: Lista de eventos en los que el personaje participa
            
        Returns:
            Character : personaje actualizado con las acciones, motivaciones y metas por cada evento
        """
        if not events:
            print("No hay eventos para simular.")
            return character
        
        str_character = character.to_dict()
        
        for i in range(len(events)):
            event = events[i]
            a_deque = deque(maxlen=5)
            m_deque = deque(maxlen=5)
            g_deque = deque(maxlen=5)
            prompt = f"""
            Generate :
            {{
                actions: (str) descripción de las acciones que el personaje realiza en este evento
                motivations: (str) motivaciones del personaje en este evento
                goals: (str) metas del personaje en este evento
            }}
            in valid JSON format, according to how would you act if your personality and traits are defined as follows:
            {str_character}
            The event is:
            {event.to_dict()}
            """
            if len(a_deque) > 0:
                prompt += f"\nYour last actions were: {', '.join(a_deque)}"
                prompt += f"\nYour last motivations were: {', '.join(m_deque)}"
                prompt += f"\nYour last goals were: {', '.join(g_deque)}"
            
            try:
                response = self.model.ask(prompt)
                if response:
                    d = self.model.clean_answer(response)
                    character.actions[event.title] = d.get("actions", "")
                    character.motivations[event.title] = d.get("motivations", "")
                    character.goals[event.title] = d.get("goals", "")

                    a_deque.append(d.get("actions", ""))
                    m_deque.append(d.get("motivations", ""))
                    g_deque.append(d.get("goals", ""))
                
            except Exception as e:
                print(f"Error al simular el personaje: {e}")
                return ""
            
        return character
    

    def simulate_event(self, event: Event, characters : List[Character]) -> List[Character]:
        """
        Simula las acciones de los personajes en base al evento dado.
        
        Args:
            characters: Lista de la clase Character que representa los personajes involucrados en el evento
            event: Evento que se simulará 
            
        """
        prompt = f"""
            Generate :
            {{characters:{{[
                    character_name (str nombre del personaje) : {{
                        actions: (str) descripción de las acciones que el personaje realiza en este evento
                        motivations: (str) motivaciones del personaje en este evento
                        goals: (str) metas del personaje en este evento
                    }},]
                }}
            }}
            in valid JSON format, depending on how each of the characters would act, being consistent with their personality in the given event.
            The event is:
            {event.to_dict()}
            The characters are described as:
        """
        print(f"Simulando el evento: {event.title}")
        for character in characters:
            last_three_actions = deque(character.actions.items(), maxlen=3)
            last_three_dict_actions = dict(last_three_actions) 

            last_three_motivations = deque(character.motivations.items(), maxlen=3)
            last_three_dict_motivations = dict(last_three_motivations) 

            last_three_goals = deque(character.goals.items(), maxlen=3)
            last_three_dict_goals = dict(last_three_goals) 

            prompt += f"""
                {character.to_dict()}
                Last three actions: {last_three_dict_actions}
                Last three motivations: {last_three_dict_motivations}
                Last three goals: {last_three_dict_goals}
                """
        try:
            resp = self.model.ask(prompt)
            # print("respuesta obtenida")
            if resp:
                d = self.model.clean_answer(resp)
                for character in characters:
                    if character.name in d.get("characters", {}):
                        char_data = d["characters"][character.name]
                        character.actions[event.title] = char_data.get("actions", "")
                        character.motivations[event.title] = char_data.get("motivations", "")
                        character.goals[event.title] = char_data.get("goals", "")
                        # print(f"Simulación para {character.name} en el evento {event.title} completada.")
                        # print(f"Acciones: {character.actions[event.title]}")
                        # print(f"Motivaciones: {character.motivations[event.title]}")
                        # print(f"Metas: {character.goals[event.title]}")

        except Exception as e:
            print(f"Error al simular el evento: {e}")
            return ""
        
        return characters
    

    def check_character_actions(self, character: Character):
        """
        Verifica la coherencia de las acciones de un personaje.
        
        Args:
            character: Instancia de la clase Character que representa al personaje
            
        Returns:
            Character: El mismo personaje pero con los cambios necesarios en las acciones para que sean coherentes con su personalidad y motivaciones.
        """
        if not character.actions:
            print(f"{character.name} no tiene acciones registradas.")
            return character, []
        
        prompt = f"""
            Generate in valid JSON format, without additional explanations:{{
                "suggested changes":[
                    {{
                        "event": (str) nombre del evento,
                        "action": (str) descripción de la acción sugerida,
                        "motivation": (str) motivación detrás de la acción,
                        "goal": (str) meta que se busca alcanzar con la acción
                    }},
                ]
                "suggested events":[
                    {{
                        "event": (str) nombre del evento sugerido,
                        "description": (str) descripción del evento
                    }},
                ]
            }}
            where you suggest (if necessary, to make the character's development consistent with their role in the story and their personality) changes to the character's actions, motivations, and goals based on the event, or the introduction of new events. If you consider them to be consistent, return the empty lists.
            The character is described as follows:
            {character.to_dict()}
        """

        actions_summary = f"{character.name}'s actions :\n"
        for event, action in character.actions.items():
            actions_summary += f"- At the event: '{event}': {action}\n"

        prompt += f"{actions_summary}"
        
        try:
            resp = self.model.ask(prompt, temperature=0.7)
            response = self.model.clean_answer(resp)
            if response:
                suggested_changes = response.get("suggested changes", [])
                suggested_events = response.get("suggested events", [])
                
                if len(suggested_changes) > 0:
                    # print(f"Sugerencias de cambios para {character.name}:")
                    for change in suggested_changes:
                        # print(f"Evento: {change['event']}, Acción: {change['action']}, Motivación: {change['motivation']}, Meta: {change['goal']}")
                        character.actions[change['event']] = change['action']
                        character.motivations[change['event']] = change['motivation']
                        character.goals[change['event']] = change['goal']
                
                if len(suggested_events) > 0:
                    # print(f"Sugerencias de nuevos eventos para {character.name}:")
                    for event in suggested_events:
                        print(f"Evento: {event['event']}, Descripción: {event['description']}")
                
                if len(suggested_events) == 0 and len(suggested_changes) == 0 :
                    print(f"{character.name} no necesita cambios en sus acciones ni nuevos eventos.")

                return character,suggested_events
        except Exception as e:
            print(f"Error al verificar las acciones del personaje: {e}")
        return character, []
                    

    def select_significant_events(self, events: List[Dict[str,str]], text: str, rules :List[str]) -> List[Event]:
        """
        Selecciona los eventos significativos para la historia de los propuestos.
        
        Args:
            events: Lista de diccionarios key: nombre del evento value: descripcion del evento
            text: Texto de la historia
            
        Returns:
            List[Event]: Lista de eventos significativos
        """
        if not events:
            print("No hay eventos para seleccionar.")
            return []
        
        prompt = f"""
            Select the events from the following list that you would add to the story without derailing the plot. There may be several or none. Return the selected events as follows, according to the provided story:
            {{
                "significant_events": [
                    {{
                        {Event._prompt}
                    }},
                ]
            }}
            In valid JSON format.
            The story is:
            {text}
            The events to be analyzed are:
            {[event for event in events]}
            Please note that the story must not violate the following rules:
            {rules}
        """
        
        try:
            response = self.model.ask(prompt, temperature=0.8)
            significant_events = self.model.clean_answer(response)
            significant_events = significant_events.get("significant_events", [])
            return [Event(**event) for event in significant_events]
        except Exception as e:
            print(f"Error al seleccionar eventos significativos: {e}")
        return []
            
       
    def add_literary_elements(self, events: List[Event], gender :str, style: str) -> List[Event]:
        """
        Añade elementos literarios a los eventos de la historia.
        
        Args:
            events: Lista de eventos a enriquecer
            
        Returns:
            List[Event]: Lista de eventos enriquecidos con elementos literarios
        """
        if not events:
            print("No hay eventos para enriquecer.")
            return []
        
        prompt = f"""
            Enrich the following events with literary elements of structure and style, theme and symbolism, character, plot, atmosphere, and tone. Add them without cluttering the story and return the enriched events in valid JSON format, considering the logical and coherent order of the plot.
            {{
                "enriched_events": [
                    {{
                        title: (str) título del evento,
                        description: (str) descripción detallada del evento con elementos narrativos
                    }},
                ]
            }}
            Please note that the following genre, tone and style are sought:
            {gender}, {style}
            The events to enrich are:
            {[f"title: {event.title} description: {event.description}" for event in events]}
        """
        
        try:
            response = self.model.ask(prompt)
            enriched_events = self.model.clean_answer(response)
            enriched_events = enriched_events.get("enriched_events", [])
            dict_enriched_events = {e["title"]: e["description"] for e in enriched_events}
            for event in events:
                if event.title in dict_enriched_events:
                    event.description = dict_enriched_events[event.title]
            return events
        except Exception as e:
            print(f"Error al enriquecer los eventos: {e}")
        return []