import csv
import datetime
import logging
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from PlotMind.PlotMind import PlotMind

# Configuración básica de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Variable global para el lock
procesamiento_lock = asyncio.Lock()

async def procesar_pedido(texto: str) -> str:
    plotMind = PlotMind()
    return plotMind.run(texto)


async def obtener_mensajes_pendientes(application):
    """Obtiene y procesa todos los mensajes pendientes"""
    logger.info("Obteniendo mensajes pendientes...")
    
    # Obtener todos los updates no procesados
    updates = await application.bot.get_updates()
    
    if not updates:
        logger.info("No hay mensajes pendientes.")
        return
    
    logger.info(f"Procesando {len(updates)} mensajes pendientes...")
    
    for update in updates:
        if update.message and update.message.text:
            try:
                texto = update.message.text
                user_id = update.message.from_user.id
                logger.info(f"Mensaje pendiente de {user_id}: {texto}")
                
                # Procesar el pedido
                respuesta = procesar_pedido(texto)
                
                # Enviar respuesta al usuario
                await application.bot.send_message(
                    chat_id=user_id,
                    text=respuesta
                )
                logger.info(f"Respuesta enviada a {user_id}")
                
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start (no requiere lock)"""
    user = update.effective_user
    await update.message.reply_text(
        f"""¡Hola {user.first_name}! 👋✨
        PlotMind es tu bot creativo para generar historias de cualquier tipo con solo enviar un mensaje. 📚🤖
        En un solo mensaje, cuéntame todos los detalles que quieres para tu historia:
        📏 Longitud (por ejemplo, 10 escenas)
        🎭 Género y tono (terror, comedia, aventura, romance…)
        👤 Personajes
        🗺️ Lugares
        🗓️ Eventos clave
        💡 ¡Y cualquier otro detalle que imagines!
        ¡Cuantos más detalles me des, más personalizada y emocionante será tu historia! 🚀📝"""
    )

# Añade estas variables globales al inicio del archivo
EVALUACION_PREGUNTAS = [
    "¿Cómo calificarías la facilidad de generar nuevas narrativas usando la herramienta (Facilidad de Uso)?\nDesde Complicado (1) hasta Fácil (10)",
    "¿Qué tan atractivo e inesperado te pareció la historia generada (Creatividad)?\nDesde Aburrido (1) hasta Creativo (10)",
    "¿En qué medida la historia representó y respondió con precisión a tu intención (Adaptabilidad)?\nDesde Insatisfactorio (1) hasta Satisfactorio (10)",
    "¿Cómo evaluarías los personajes y la trama de la historia en términos de su credibilidad, coherencia y atractivo (Fiabilidad)?\nDesde No Interesante (1) hasta Interesante (10)",
    "En general, ¿qué tan satisfecho estás con la historia generada (Satisfacción)?\nDesde No Satisfecho (1) hasta Satisfecho (10)"
]

# Diccionario para guardar las evaluaciones en curso
evaluaciones_en_curso = {}

async def enviar_pregunta_evaluacion(chat_id, context, pregunta_actual=0, respuestas=None):
    if respuestas is None:
        respuestas = {}
    
    if pregunta_actual < len(EVALUACION_PREGUNTAS):
        # Guardar estado actual en el contexto
        evaluaciones_en_curso[chat_id] = {
            'pregunta_actual': pregunta_actual,
            'respuestas': respuestas,
            'mensaje_original': evaluaciones_en_curso.get(chat_id, {}).get('mensaje_original', "")
        }
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=EVALUACION_PREGUNTAS[pregunta_actual]
        )
    else:
        # Todas las preguntas respondidas
        await guardar_evaluacion_completa(chat_id, respuestas)
        await context.bot.send_message(
            chat_id=chat_id,
            text="¡Gracias por tu evaluación! Tus respuestas han sido registradas." \
            " Si deseas realizar otra historia, simplemente envía un nuevo mensaje con la descripción."
        )
        del evaluaciones_en_curso[chat_id]

async def guardar_evaluacion_completa(chat_id, respuestas):
    """Guarda la evaluación completa en un archivo CSV, manteniendo datos existentes"""
    mensaje_original = evaluaciones_en_curso.get(chat_id, {}).get('mensaje_original', "")
    
    # Datos a guardar
    datos = {
        'timestamp': datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S'),
        'chat_id': chat_id,
        'mensaje_original': mensaje_original,
        **respuestas  # Desempaqueta todas las puntuaciones
    }
    
    # Nombre del archivo CSV
    csv_file = 'evaluaciones.csv'
    
    # Cabeceras del CSV (basadas en las claves de los datos)
    fieldnames = [
        'timestamp',
        'chat_id',
        'mensaje_original',
        'Facilidad de Uso',
        'Creatividad',
        'Adaptabilidad',
        'Fiabilidad',
        'Satisfacción'
    ]
    
    try:
        # Verificar si el archivo existe
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Escribir cabecera solo si el archivo no existe o está vacío
            if not file_exists or file.tell() == 0:
                writer.writeheader()
            
            # Escribir los datos
            writer.writerow(datos)
            
        logger.info(f"Evaluación guardada en CSV: {datos}")
        
    except Exception as e:
        logger.error(f"Error al guardar evaluación en CSV: {e}")
        # Opcional: Reintentar o notificar al administrador

async def handle_evaluacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        texto = update.message.text
        
        # Verificar si es una respuesta de evaluación (número del 1 al 10)
        if chat_id in evaluaciones_en_curso and texto.isdigit():
            puntuacion = int(texto)
            if 1 <= puntuacion <= 10:
                estado_actual = evaluaciones_en_curso[chat_id]
                pregunta_actual = estado_actual['pregunta_actual']
                respuestas = estado_actual['respuestas']
                
                # Guardar la respuesta
                categoria = [
                    "Facilidad de Uso",
                    "Creatividad",
                    "Adaptabilidad",
                    "Fiabilidad",
                    "Satisfacción"
                ][pregunta_actual]
                
                respuestas[categoria] = puntuacion
                
                # Enviar siguiente pregunta
                await enviar_pregunta_evaluacion(
                    chat_id, 
                    context, 
                    pregunta_actual + 1, 
                    respuestas
                )
                return
            else:
                await update.message.reply_text("Por favor, ingresa un número entre 1 y 10.")
                return
    except Exception as e:
        logger.error(f"Error procesando evaluación: {e}")

# Modifica la función handle_message para iniciar la evaluación después de responder
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    texto = update.message.text
    
    # Verificar si es una respuesta de evaluación (número del 1 al 10)
    if texto.isdigit() and 1 <= int(texto) <= 10:
        return  # Deja que handle_evaluacion maneje esto
    
    # Verificar si es un comando (no aplicar lock a comandos)
    if texto.startswith('/'):
        return  # Los comandos son manejados por sus handlers específicos
    
    mensaje_procesando = await update.message.reply_text(
        "🛠️ Estoy creando tu historia...\n"
        "Esto puede tomar varios minutos dependiendo de la complejidad y la generación de otras historias.\n"
        "¡Te avisaré cuando esté listo!"
    )
    async with procesamiento_lock:  # Solo aplica lock a procesamiento de pedidos
        try:
            respuesta = await procesar_pedido(texto)
            
            # Dividir la respuesta en partes si es muy larga
            max_chars = 3000
            if len(respuesta) > max_chars:
                partes = respuesta.split('\n\n')
                partes_finales = []
                for parte in partes:
                    if len(parte) > max_chars:
                        for i in range(0, len(parte), max_chars):
                            partes_finales.append(parte[i:i+max_chars])
                    else:
                        partes_finales.append(parte)
                
                # Eliminar mensaje de "procesando" antes de enviar las partes
                await context.bot.delete_message(chat_id=user_id, message_id=mensaje_procesando.message_id)
                
                for i, parte in enumerate(partes_finales, 1):
                    await update.message.reply_text(
                        f"Parte {i}/{len(partes_finales)}:\n\n{parte}"
                    )
                    await asyncio.sleep(0.5)
            else:
                # Eliminar mensaje de "procesando" y enviar respuesta completa
                await context.bot.delete_message(chat_id=user_id, message_id=mensaje_procesando.message_id)
                await update.message.reply_text(respuesta)
            
            evaluaciones_en_curso[user_id] = {
                'mensaje_original': texto,
                'pregunta_actual': 0,
                'respuestas': {}
            }
            await enviar_pregunta_evaluacion(user_id, context)
            
        except Exception as e:
            logger.error(f"Error al procesar pedido: {e}")
            # Asegurarse de eliminar el mensaje de "procesando" incluso si hay error
            await context.bot.delete_message(chat_id=user_id, message_id=mensaje_procesando.message_id)
            await update.message.reply_text("❌ Ocurrió un error al procesar tu solicitud. Por favor, inténtalo de nuevo.")

def main():
    """Configura y ejecuta el bot"""
    # Crear aplicación
    application = Application.builder().token(TOKEN).build()
    
    # Manejar comandos (se ejecutan inmediatamente)
    application.add_handler(CommandHandler("start", start))
    
    # Primero añadir el handler de evaluaciones (con mayor prioridad)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r'^[1-9]|10$'), 
        handle_evaluacion
    ))
    
    # Luego añadir el handler de mensajes normales (con menor prioridad)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # Procesar mensajes pendientes al iniciar
    application.run_polling(close_loop=False)
    loop = application.running_loop
    loop.create_task(obtener_mensajes_pendientes(application))
    
    logger.info("Bot iniciado. Presiona Ctrl+C para detenerlo.")
    application.run_polling()

if __name__ == "__main__":
    main()