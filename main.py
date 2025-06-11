from ConversationalAgents.Gemini import Gemini
from PlotMind.PlotMind import PlotMind

if __name__ == "__main__":
    # Configura tu API key de Gemini
    
    prompts= ["""
        Fantasía Épica (Tono: Grandioso/Melancólico)
        Objetivo central: Un guerrero caído debe recuperar el "Corazón de Eldrin", una gema que contiene el último suspiro de los dioses, antes de que un culto lo use para reescribir la realidad.
        Personajes:
        Kael Aranthir (protagonista): Medio elfo con cicatrices luminosas; atormentado por visiones de un futuro donde su espada mata a quien ama.
        Syndra la Tejedora (antagonista): Líder del culto, capaz de manipular recuerdos; usa un manto hecho de sombras vivas.
        Secundarios: Un mercenario enano que solo habla en preguntas; un fantasma niño que guía a Kael en sueños.
        Objetos clave:
        El Lamento de Valtherion (espada que sangra cuando miente su portador).
        Mapa de la Ciudad Flotante, escrito en piel de dragón.
        Ubicaciones:
        Las Ruinas de Mournthar: Estatuas que susurran secretos en lenguas muertas.
        El Umbral de los Dioses: Un puente de huesos sobre un abismo sin fondo.
        Comienzo opcional:
        "El día que Kael encontró la espada, supo que estaba condenado. No por su filo, sino por el sonido que hacía al desenvainarse: el llanto de su hermano muerto."
        Eventos sugeridos: 8 """,
        """
        Misterio Sobrenatural (Tono: Claustrofóbico/Paranoico)
        Objetivo central: Una periodista investiga una serie de suicidios en un hotel abandonado, donde cada víctima dejó grabaciones de voz idénticas pese a morir en décadas distintas.
        Personajes:
        Vera Cross (protagonista): Tatuajes de símbolos ocultos (invisibles bajo luz normal); adicta a la verdad.
        El Huésped 207 (antagonista): Figura que aparece en fotos antiguas, siempre de espaldas; su sombra no coincide con su cuerpo.
        Secundarios: Un conserje que insiste en que "el hotel no tiene sótano"; una niña fantasma que juega al escondite con pistas reales.
        Objetos clave:
        Grabadora de cera (reproduce mensajes del futuro).
        Llave 207: Se oxida cuando alguien miente cerca de ella.
        Ubicaciones:
        Hotel Eclipso: Pasillos que cambian de posición; el espejo del lobby refleja a los muertos.
        Sótano prohibido: Paredes cubiertas de nombres escritos al revés.
        Comienzo opcional:
        "La primera grabación decía 'No confíes en tu reflejo'. La segunda también. Y la tercera. Pero Vera jamás había hablado esas palabras."
        Eventos sugeridos: 6 
        """,
        """
        Ciencia Ficción Cyberpunk (Tono: Cínico/Neon)
        Objetivo central: Un hacker con memoria implantada debe descifrar un código que borró su pasado, mientras una corporación le persigue para recuperar "el Archivo Zero": un algoritmo que predice revoluciones sociales.
        Personajes:
        Rook (protagonista): Ojos biónicos con fallos que le muestran recuerdos ajenos; viste una gabardina que cambia de color según su estado de ánimo.
        Director Kovacs (antagonista): CEO de NeuroSpan; su voz es un coro de sus 12 clones muertos.
        Secundarios: Un taxista IA que filosofa sobre el libre albedrío; una niña callejera que vende "emociones pirata".
        Objetos clave:
        Chip Mnemósine (contiene memorias de Rook, pero ninguna es suya).
        Disco de Nix: Almacena el Archivo Zero; se autodestruye si alguien lo mira directamente.
        Ubicaciones:
        Torre Azur: Edificio que existe en 3 ubicaciones simultáneas.
        El Barrio Holograma: Calles donde el graffiti cobra vida.
        Comienzo opcional:
        "Rook sabía dos cosas: que su nombre era falso, y que alguien había pagado 5 millones por borrarlo. Lo demás era código corrupto."
        Eventos sugeridos: 7
        """,
        """
        Romance Gótico (Tono: Obsesivo/Sensual)
        Objetivo central: Una restauradora de arte se enamora del espíritu de un pintor maldito, pero su obsesión por liberarlo desata una plaga de cuadros que devoran recuerdos.
        Personajes:
        Elaine Voss (protagonista): Siempre huele a trementina; tiene los ojos de distinto color (uno refleja el pasado).
        Lucian Duvall (antagonista/amante): Fantasma atrapado en su autorretrato; su sonrisa desaparece cuando miente.
        Secundarios: Una rival que colecciona lágrimas de amantes; un gato que solo es visible en espejos.
        Objetos clave:
        Pincel de Duvall: Pinta con sangre y nunca se seca.
        Espejo de la Viuda: Muestra el futuro, pero solo tragedias.
        Ubicaciones:
        Mansión Blackthorn: Las flores del jardín crecen en forma de retratos.
        Galería Nocturna: Abre a medianoche; sus visitantes nunca recuerdan haber estado allí.
        Comienzo opcional:
        "Elaine no supo cuándo dejó de restaurar el cuadro y empezó a conversar con él. Pero una mañana, el retrato de Lucian le había devuelto el saludo."
        Eventos sugeridos: 5 
        """,
        """Western Fantástico (Tono: Brutal/Onírico)
        Objetivo central: Un pistolero con un revólver que dispara sueños debe enfrentar a una banda de forajidos inmortales en un pueblo donde la leyenda se vuelve real.
        Personajes:
        Jericho Holt (protagonista): Cicatriz en forma de serpiente que se mueve; fuma tabaco que induce visiones.
        El Reverendo (antagonista): Predicador que resucita cada luna llena; su Biblia está escrita en piel humana.
        Secundarios: Una mujer-coyote que comercia con nombres; un sheriff hecho de arena.
        Objetos clave:
        Peacemaker (revólver que convierte balas en pesadillas).
        Reloj de Sol Negro: Avanza hacia atrás durante los crímenes.
        Ubicaciones:
        Pueblo Fantasma de Silver Gulch: Sus habitantes son ecos de muertos violentos.
        El Cañón del Silencio: Donde los gritos salen como susurros años después.
        Comienzo opcional:
        "Jericho sabía que el Reverendo era inmortal. Lo había matado seis veces. Pero el séptimo disparo siempre es diferente."
        Eventos sugeridos: 6 """]
    
    prompt_alternativo = """
        Juego de Tronos - El Invierno y la Guerra por el Trono
        Contexto:
        La penúltima temporada de Juego de Tronos marca el inicio del invierno y la convergencia de las tramas principales. Los Caminantes Blancos avanzan hacia el Muro, Daenerys Targaryen llega a Poniente para reclamar el Trono de Hierro, y las alianzas se tambalean entre traiciones y revelaciones. La temporada culmina con la caída del Muro y la unión forzada de ejércitos contra el verdadero enemigo: el Rey de la Noche.
        Personajes Principales:
        Daenerys Targaryen:
            Ubicación: Rocadragón.
            Estado: Ha llegado a Poniente con sus dragones, los Inmaculados y los Dothrakis. Busca aliados para enfrentarse a Cersei, pero su enfoque cambia al conocer la amenaza de los Caminantes Blancos.
            Eventos clave:
            Quema el ejército Lannister en la Batalla de la Cosecha Dorada.
            Pierde a Viserion, convertido en un dragón zombie por el Rey de la Noche.
            Se une románticamente a Jon Snow (sin saber que son tía y sobrino) 39.
        Jon Snow:
            Ubicación: Invernalia.
            Estado: Rey en el Norte, pero renuncia al título para aliarse con Daenerys. Descubre su verdadero linaje (hijo de Rhaegar Targaryen y Lyanna Stark) gracias a Bran y Sam.
            Eventos clave:
            Viaja a Rocadragón para pedir ayuda contra los Caminantes Blancos.
            Participa en la expedición más allá del Muro para capturar un espectro y demostrar la amenaza a Cersei.
            Se une a Daenerys, tanto política como románticamente.
        Cersei Lannister:
            Ubicación: Desembarco del Rey.
            Estado: Reina de los Siete Reinos tras destruir el Septo de Baelor. Embarazada de Jaime, pero planea traicionar a todos para mantener el poder.
            Eventos clave:
            Se reúne con Daenerys y Jon en el Cónclave de Pozo Dragón.
            Finge apoyar la tregua contra los muertos, pero contrata a la Compañía Dorada con Euron Greyjoy.
        Tyrion Lannister:
            Ubicación: Al lado de Daenerys como su Mano.
            Estado: Estratega principal, pero sus planes fallan. Se preocupa por el giro violento de Daenerys.
        Sansa Stark:
            Ubicación: Invernalia.
            Estado: Señora de Invernalia, enfrenta tensiones con Arya y descubre la traición de Meñique, quien es ejecutado.
        Arya Stark:
            Ubicación: Regresa a Invernalia tras entrenar con los Hombres Sin Rostro.
            Estado: Asesina a los Frey y planea vengar a su familia. Se reconcilia con Sansa.
        Bran Stark:
            Ubicación: Invernalia.
            Estado: Ahora es el Cuervo de Tres Ojos. Revela el parentesco de Jon y descubre la debilidad de los Caminantes Blancos (el Rey de la Noche está vinculado a él).
        Jaime Lannister:
            Ubicación: Abandona Desembarco del Rey tras ver la locura de Cersei.
            Estado: Cabalga hacia el Norte para unirse a la lucha contra los muertos.
        El Rey de la Noche:
            Ubicación: Más allá del Muro.
            Estado: Destruye el Muro con Viserion zombie en el cliffhanger final.

        Escenarios Clave:
        Rocadragón: residencia hace siglos de los Targaryen, se encuentra ubicada en una isla cerca de Desembarco del Rey.
        Pozo Dragón (Cónclave) : ubicado dentro de Desembarco del Rey.
        Más allá del Muro : zona al norte del Muro
        Batalla de la Cosecha Dorada : cerca de Roca Casterly, residencia de los Lannister.
        Invernalia : residencia desde hace siglos de los Stark.

        Temas Centrales:
        Alianzas frágiles: La tregua entre Daenerys y Cersei es una mentira.
        Identidad y legado: Jon descubre su verdadero nombre (Aegon Targaryen).
        El costo del poder: Daenerys comienza a mostrar rasgos de su padre, el Rey Loco.
        La verdadera guerra: Los vivos vs. los muertos.

        Objetivo:
        NO SIGAS LA TRAMA DE LA SERIE, CREA UNA TEMPORADA ALTERNATIVA A PARTIR DE LOS EVENTOS DESCRITOS.
        Incluir giros inesperados, traiciones y momentos de redención, manteniendo la esencia oscura y política de la serie, hazlo en 50 eventos.
    """
    
    # for p in prompts[2:]:
    #     pm = PlotMind()
    #     pm.run(p)

    #     print(pm.model.ask("Eres un narrador experto. Crea una historia con siguiente prompt: " + p))
 

    pm = PlotMind()
    pm.run(prompt_alternativo)


