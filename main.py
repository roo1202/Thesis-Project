from PlotMind.PlotMind import PlotMind

if __name__ == "__main__":
    # Configura tu API key de Gemini
    
    
    # Texto narrativo de ejemplo
    SAMPLE_TEXT = """
    La literatura no es un mero juego de palabras; lo que importa es lo que no queda dicho, o lo que puede ser leído entre líneas

    Narración en tercera persona limitada (saltando entre los protagonistas).
    Tonos crudos y poéticos, con diálogos cortantes y descripciones vívidas.
    Giros dramáticos: Muertes inesperadas, traiciones y revelaciones que redefinen la trama.
    Escribe 50 capítulos de esta historia, intercalando las perspectivas de Aric, Lysara y Tharion. Muestra cómo sus tramas colisionan durante un banquete en Vortheas, donde un asesinato desencadena una crisis política. Incluye símbolos recurrentes (como un cuervo con ojos de plata) y diálogos que insinúen la profecía.

    En el continente fracturado de Etherion, donde reinos antiguos se desmoronan bajo el peso de la ambición, la traición y fuerzas sobrenaturales, cinco protagonistas luchan por sobrevivir, gobernar o destruir un mundo al borde del caos. Sus destinos se entrelazan a través de guerras, alianzas frágiles y secretos ancestrales.
    Personajes Principales:
    Aric de Valderrák (El Rey Destronado):
    Último heredero de un reino conquistado, vive exiliado mientras recluta un ejército de mercenarios y nobles descontentos para recuperar su trono.
    Trama: Deberá elegir entre su sed de venganza o salvar a Etherion de una amenaza mayor.
    Lysara Valtys (La Tejedora de Sombras):
    Espía maestra y bastarda de una casa noble, manipula las cortes desde las sombras. Sabe un secreto que podría incendiar los Siete Reinos.
    Trama: Su lealtad se divide entre su familia y una sociedad secreta que busca controlar el mundo.
    Tharion el Maldito (El Guerrero de los Abismos):
    Un general condenado por un ritual oscuro, ahora lleva una armadura viviente que consume su humanidad. Comanda un ejército de no muertos.
    Trama: Busca redimirse o arrastrar a todos a su condena.
    Elia de las Brumas (La Bruja de los Hielos):
    Joven sacerdotisa de un dios olvidado, descubre que su magia proviene de una entidad primordial que desea ser liberada.
    Trama: Debe decidir si usar su poder para sanar o destruir.
    Kael the Ironmonger (El Mercader de Guerra):
    Un comerciante sin escrúpulos que financia ambos bandos de la guerra. Su red de intrigas es clave para el control de Etherion.
    Trama: Un asesinato lo obliga a huir, revelando una conspiración que él mismo ayudó a crear.
    Tramas Principales:
    La Guerra de los Cinco Cuervos: Tres casas nobles se disputan el trono vacante de la capital, Vortheas, mientras facciones ocultas manipulan el conflicto.
    El Despertar de los Primigenios: Criaturas antiguas, selladas bajo las montañas, comienzan a influir en los sueños de los poderosos.
    La Profecía del Eclipse Sangriento: Un evento cósmico que podría cambiar el balance de poder para siempre.


    """

    t = "quiero que tenga 20 pasajes, hayan muchos giros inesperados y muchos objetos reveladores y para despistar"
    
    pm = PlotMind()
    pm.run()

 
