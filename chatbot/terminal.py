import uuid
import asyncio
from dotenv import load_dotenv

from llm_provider import get_llm
from langgraph.checkpoint.memory import MemorySaver

from logger import logger
from workflow.chat_runner import ChatRunner

# Cargar variables de entorno
load_dotenv()

async def run_terminal_chat():
    """
    Inicializa y ejecuta un bucle de chat interactivo en la terminal.
    """
    session_id = str(uuid.uuid4())

    logger.debug("--- Asistente de Admisión (Terminal) ---")
    logger.debug("El asistente se está inicializando...")

    try:
        # Inicializar el runner y el grafo subyacente
        memory = MemorySaver()
        llm = get_llm()
        runner = ChatRunner(llm, memory, session_id)
        logger.debug("¡Asistente listo! Escribe 'salir' para terminar.")
        print("-" * 40)

    except Exception as e:
        logger.critical(f"Error fatal durante la inicialización: {e}", exc_info=True)
        return

    while True:
        try:
            prompt = await asyncio.to_thread(input, "Tú: ")
            if prompt.lower() in ["salir", "exit", "quit"]:
                print("--- Fin de la sesión ---")
                break

            if not prompt.strip():
                continue

            # Llamar al manejador de mensajes del grafo
            response = await runner.handle_message(prompt)
            
            print(f"Asistente: {response}")

        except KeyboardInterrupt:
            logger.debug("Fin de la sesión (interrupción manual).")
            break
        except Exception as e:
            logger.error(f"Ocurrió un error durante la ejecución: {e}", exc_info=True)            

if __name__ == "__main__":
    asyncio.run(run_terminal_chat())