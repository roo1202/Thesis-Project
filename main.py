from ConversationalAgents.DeepSeek import DeepSeek
from PlotMind.PlotMind import PlotMind

if __name__ == "__main__":
    # Configura tu API key de Gemini
    
    
    # Texto narrativo de ejemplo
    SAMPLE_TEXT = """
    La carta llegó un martes de lluvia, cuando el reloj de la torre marcaba una hora que no existía.
    El sobre, amarillento por el tiempo, llevaba mi nombre escrito en una caligrafía que reconocí al instante: la de Daniel Hargrove, mi abuelo, desaparecido veinte años atrás en circunstancias que aún helaban las reuniones familiares. Lo extraño no era que me escribiera después de dos décadas, sino que la fecha del matasellos coincidiera con ayer.
    Al abrirlo, solo encontré una llave oxidada y una fotografía en blanco y negro. En ella, nuestro viejo caserón familiar aparecía con una puerta que jamás había existido: un arco de piedra tallada con símbolos que se retorcían como serpientes bajo la luz de la luna. Lo peor no fue lo imposible de la imagen, sino el detalle que noté al inclinarla. Alguien había tachado con tinta roja los rostros de todos los retratados, incluido el mío.
    Y entonces, el teléfono sonó. Del otro lado, solo se escuchaba una voz susurrante que repetía tres palabras:
    "Ya es tarde."
    El reloj de la torre volvió a dar la hora. Esta vez, las agujas giraban al revés.

    La literatura no es un mero juego de palabras; lo que importa es lo que no queda dicho, o lo que puede ser leído entre líneas

    """

    t = "quiero que tenga 20 pasajes, hayan muchos giros inesperados y muchos objetos reveladores y para despistar"
    
    pm = PlotMind()
    pm.run()

 
