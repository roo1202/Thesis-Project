from PlotMind.PlotMind import PlotMind

if __name__ == "__main__":
    # Configura tu API key de Gemini
    
    
    # Texto narrativo de ejemplo
    SAMPLE_TEXT = """
    La literatura no es un mero juego de palabras; lo que importa es lo que no queda dicho, o lo que puede ser leído entre líneas

    """

    t = "quiero que tenga 20 pasajes, hayan muchos giros inesperados y muchos objetos reveladores y para despistar"
    
    pm = PlotMind()
    pm.run()

 
    text = """

    En este capítulo se detalla el proceso de implementación del sistema de generación automática de historias desarrollado. Se presentan las decisiones de diseño arquitectónico, las clases principales que componen el sistema, así como los algoritmos y técnicas específicas empleadas. La arquitectura del sistema se implementó siguiendo los componentes del modelo conceptual, de manera que por cada componente se desarrolló un módulo independiente, permitiendo flexibilidad y escalabilidad al modelo.

    StorySpace:

    En el mundo o espacio de la historia, se definen las clases que caracterizan a cada una de las entidades que intervienen en la misma. Se define como base la clase Entity para definir algunos comportamientos en común, y sus herederas:
    
    -Character: Representa un personaje en la historia, con atributos estáticos como el nombre, el rol, la personalidad, la historia del personaje y su apariencia. Posee otros atributos como sus metas, motivaciones y acciones, que se almacenan en diccionarios cuya llave es el nombre del evento en que se presentan.

    -Location: Representa una ubicación dentro de la historia. El lugar se describe por un nombre, una descripción, una historia, referencias a lugares que conectan con el mismo, etc.

    -Item: Representa un objeto de la historia con nombre, tipo de objeto, descripción, propiedades que posee, efectos en los personajes o el mundo, habilidades que requiera su uso, etc.

    -Event: Representa un evento de la historia con atributos como: un título, una descripción del evento o acontecimiento, referencias al lugar donde se desarrolla el evento y otras ubicaciones que se mencionen, referencias a personajes y objetos involucrados, efectos en el mundo de la historia, etc.

    Story Graph Generator :

    El módulo del Generador del grafo de la historia está conformado por tres clases que se encargan de construir el grafo inicial: EntityRecognition, RelationshipManager y GraphGenerator.

    GraphGenerator: 
    Esta clase se inicializa creando un multigrafo con la biblioteca networkx, en el que se añaden los nodos de eventos a medida que se generan, además de los distintos arcos que pueden existir entre estos. Posteriormente, se incluyen y se vinculan a los vértices de eventos nuevos nodos de personajes, objetos y lugares para ciertos análisis de trama que se explicarán más adelante. Mediante el método visualize_graph se muestra una interfaz interactiva del grafo usando la biblioteca pyvis.

    EntityRecognition:
    Se encarga de la extracción de entidades en textos, mediante la interacción con un agente conversacional. Métodos como: extract_entities e indentify_entities se encargan de extraer información estructurada del texto en lenguaje natural. Se generan prompts dinámicos para especificar al agente los personajes, objetos, ubicaciones y eventos a extraer, además de la estructura deseada.

    RelationshipManager:
    Clase encargada de inferir y almacenar las relaciones entre los eventos y las entidades.  Se crean prompts dinámicos al igual que en EntityRecognition, y se almacenan las relaciones de manera eficiente para facilitar la búsqueda posterior por entidades. Además de esta, se definen clases como Relationship y EntityRelationship para describir la relación con ciertos atributos.

    DramaManager:

    El gestor de drama es el encargado de añadir elementos y enriquecer la trama de la historia. Cuenta con metodos como: improve_characters, improve_locations e improve_items; encargados de mejorar y completar los personajes, las ubicaciones y los objetos respectivamente. Dada la historia -en el punto de generacion que se encuentre- y las entidades que se quieren expandir, se crean prompts donde se describen las caracteristicas que ya poseen estas entidades y las que se quieren generar, tomando como guia la historia para que se generen a corde a esta.

    Se siguieron dos enfoques para la simulaciones de los personajes en la historia. Un enfoque se desarrolla mediante el metodo simulate_character, que simula el comportamiento del personaje en una secuencia de eventos, conociendo todas las caracteristicas del personaje y la descripcion del suceso o evento. Otro enfoque fue mediante el metodo simulate_event, que simula el comportamiento de todos los personajes que intervienen en un evento dado. En este no se conoce el proximo evento, ya que se simula uno a la vez, pero sí se conocen las metas, motivaciones y acciones pasadas de los personajes.

    Para el chequeo de coherencia en los arcos dramaticos de los personajes se implemento el metodo check_character_actions, el cual devuelve un nivel de coherencia para las acciones de cada personaje, conociendo sus motivaciones y metas. Tambien sugiere modificaciones en el comportamiento del personaje ante algunos eventos y nuevos eventos para añadir a la trama, que permitan un mayor desarrollo del personaje. Estos eventos son tenidos en cuenta para balancear la trama con los objetivos de los personajes.

    Cada personaje puede sugerir nuevos eventos al grafo de la historia, pero no todos son elegidos, ya que dichos eventos pueden ser contradictorios respecto a la trama principal o a los objetivos del autor (por ejemplo el antagonista puede sugerir eventos donde mate al protagonista). Para seleccionar de estos eventos los que realmente aportan a la trama sin crear contradicciones, se usa el metodo select_significant_events, que contextualiza al agente conversacional con la historia y los eventos sugeridos.

    Finalmente se recorren los eventos de la trama y se añade a la descripcion de algunos de ellos anotaciones de elementos narrativos segun sea conveniente con el tono, el estilo y el genero de la historia para posteriorimente generar el texto narrativo.

    DependencyManager

    """