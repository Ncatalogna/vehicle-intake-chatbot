from typing import List, Literal
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSerializable
from workflow.orchestrator_state import NextNode, OrchestratorState, ClientResult, VehicleResult
from logger import logger
from langchain_core.messages import SystemMessage

class SupervisorResponse(BaseModel):
    """
    Esquema genérico. El supervisor determina la intención y extrae
    la información como una lista de strings, sin interpretación.
    """
    intent_description: str = Field(
        description="Una descripción breve y en lenguaje natural de la intención principal del usuario."
    )
    # NOTE: Se evita el uso de `Enum` y `List` en los esquemas Pydantic para `with_structured_output` debido a problemas de inestabilidad y fallos reportados en LangChain/LangGraph.
    #
    # 1. Inestabilidad con `Enum`: Se han documentado crashes, especialmente al usar modelos de Gemini. El framework puede fallar al procesar el esquema o al manejar valores de enumeración no reconocidos devueltos por la API.
    #    - LangChain Issue #33444: Reporta un crash (`AttributeError: 'int' object has no attribute 'name'`) debido a un valor de `FinishReason` (un tipo de Enum) no reconocido de la API de Gemini.[1]
    #    - LangChain Discussion #28778: Los usuarios reportan que el uso de `Enum` en la especificación de salida estructurada causa un crash directo con Gemini.[2]
    #
    # 2. Complejidad con `List`: El tipo `List` puede amplificar los problemas de tipos anidados. Si un `Enum` o un sub-modelo es propenso a errores, una `List` de esos elementos aumenta la probabilidad de un fallo de validación y complica la depuración.
    #    - LangGraph Issue #5665: Demuestra cómo los esquemas de `with_structured_output` (que pueden contener `List`) usados dentro de una herramienta pueden "filtrarse" y causar errores en el agente principal (`ValueError: Found AIMessages with tool_calls that do not have a corresponding ToolMessage`).[3]
    next_node: str = Field(
        description= (
            "La mejor ruta definida en (NextNode) a seguir basada en la intención del usuario.\n"
            f"{NextNode.COLLECT_CLIENT_DATA.value}\n"
            f"{NextNode.CONFIRM_CLIENT_DATA.value}\n"
            f"{NextNode.COLLECT_VEHICLE_DATA.value}\n"
            f"{NextNode.CONFIRM_VEHICLE_DATA.value}\n"
            f"{NextNode.CHECK_ELIGIBILITY.value}\n"
            f"{NextNode.GENERATE_RESPONSE.value}\n"
            f"{NextNode.FALLBACK.value}"
        )
    )
    extracted_data: List[str] = Field(
        default_factory=list,
        description=(
            "Una lista de todos los fragmentos de datos (strings) extraídos del mensaje del usuario. "
            "El supervisor NO valida, interpreta ni categoriza los datos, solo los extrae tal cual."
        )
    )

def create_supervisor_agent(
    llm: BaseChatModel
) -> RunnableSerializable:
    """
    Crea el agente supervisor que estructura la entrada y elige el siguiente paso.
    """
    system_prompt_template = (
        "Eres un agente supervisor experto. Tu función es dirigir el flujo de la conversación.\n\n"        
        "**Reglas de Decisión**:\n"
        "1.  **Si el flujo es 'Recolectando datos'**: La respuesta del usuario es la información para la 'Última Pregunta'. Tu `intent_description` debe ser 'Usuario proporciona el dato solicitado'. Extrae la respuesta del usuario tal cual en `extracted_data` y elige el `next_node` de recolección de datos.\n"
        "2.  **Si el flujo es 'Esperando confirmación'**: La respuesta es 'sí' o 'no'. Describe la intención como 'Usuario confirma o niega datos' y elige el nodo de confirmación.\n"
        "3.  **Si no hay una 'Última Pregunta'**: Analiza la intención del usuario de forma general.\n\n"
        "**Reglas de Intencionalidad**:\n"
        "1. `intent_description` es una combinacion de lo ingresado del usuario combinado en caso de disponer Última pregunta hecha al usuario."
        "**Tu Tarea**:\n"
        "1.  Describe la `intent_description` de forma específica.\n"
        "2.  Extrae los datos crudos en `extracted_data`.\n"
        "3.  Elige el `next_node` más apropiado de las opciones.\n\n"
        "**Contexto Clave:**\n"
        "- Flujo Actual: {flow_context}.\n"
        "- Última Pregunta al Usuario: {last_question}.\n\n"
        "{routing_rules_prompt}"
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt_template),
            ("placeholder", "{message}"),
        ]
    )

    structured_llm = llm.with_structured_output(SupervisorResponse)
    
    agent = prompt | structured_llm
    return agent

def is_client_complete(client: ClientResult | None) -> bool:
    """Verifica si todos los campos del cliente están completos."""
    if not client:
        return False
    
    required_fields = [
        "id", "name", "last_name", "birth_date", "documento", 
        "documento_type", "email", "phone_number"
    ]
    
    return all(getattr(client, field) is not None for field in required_fields)

def is_vehicle_complete(vehicle: VehicleResult | None) -> bool:
    """Verifica si todos los campos del vehículo, incluido su ID, están completos."""
    if not vehicle:
        return False
    
    required_fields = [
        "id", "license_plate", "brand", "model", "year"
    ]
    
    return all(getattr(vehicle, field) is not None for field in required_fields)

def supervisor_node(
    state: OrchestratorState,
    agent: RunnableSerializable
) -> dict:
    """
    Nodo que ejecuta el supervisor y actualiza el estado.
    """
    logger.debug("---SUPERVISOR---")
    
    message = state.get("message", "")
    client_data = state.get("client")
    vehicle_data = state.get("vehicle")
    
    last_question_list = state.get("base_message", [])
    last_question_str = "\n".join(last_question_list) if last_question_list else "Ninguna"

    determined_next_node: NextNode | None = None
    generic_next_node = False
    flow_context: str
    routing_rules_prompt = ""

    if is_client_complete(client_data):
        if is_vehicle_complete(vehicle_data):            
            notify_elegibility = state.get("notify_elegibility", False)                
            if notify_elegibility:
                generic_next_node = True
                # La recolección ya terminó en un turno anterior, ahora se ofrece flexibilidad.
                flow_context = "El proceso de recolección de datos ha finalizado. Puedes solicitar la verificación de elegibilidad o realizar otra acción."                
                all_nodes = [f"   - '{node.value}'" for node in NextNode if node not in [NextNode.FALLBACK, NextNode.GENERATE_RESPONSE]]
                routing_rules_prompt = "**Opciones de Siguiente Nodo (NextNode):**\n" + "\n".join(all_nodes)
            else:
                # Es la primera vez que se completan todos los datos. El flujo es estricto.
                flow_context = "Proceso de recolección finalizado. El siguiente paso es evaluar la elegibilidad."
                determined_next_node = NextNode.CHECK_ELIGIBILITY            
        elif state.get("confirmation_request"):
            flow_context = "Esperando confirmación de los datos del vehículo"
            determined_next_node = NextNode.CONFIRM_VEHICLE_DATA
        else:
            flow_context = "Recolectando datos del vehículo"
            determined_next_node = NextNode.COLLECT_VEHICLE_DATA
    elif state.get("confirmation_request"):
        flow_context = "Esperando confirmación de los datos del cliente"
        determined_next_node = NextNode.CONFIRM_CLIENT_DATA
    else:
        flow_context = "Recolectando datos del cliente"
        determined_next_node = NextNode.COLLECT_CLIENT_DATA
    
    flow_context_with_suggestion = (
        f"{flow_context}."
        + (f" El siguiente paso sugerido es '{determined_next_node.value}'." if determined_next_node else "")
    )

    try:
        parsed_response = agent.invoke({
            "message": message,
            "routing_rules_prompt": routing_rules_prompt,
            "last_question": last_question_str,
            "flow_context": flow_context_with_suggestion
        })

        if not parsed_response:
            raise ValueError("No se pudo obtener una respuesta estructurada del supervisor.")

        logger.debug(f"---SUPERVISOR: Intención Descrita -> \"{parsed_response.intent_description}\" ---")
        logger.debug(f"---SUPERVISOR: Datos Crudos Extraídos -> {parsed_response.extracted_data} ---")
        
        if generic_next_node:
            next_node_str = parsed_response.next_node
            try:
                determined_next_node = NextNode(next_node_str)
            except ValueError:
                logger.warning(f"---SUPERVISOR: Valor de next_node inválido '{next_node_str}', usando fallback. ---")
                determined_next_node = NextNode.FALLBACK

        update_dict = {
            "next_node": determined_next_node,
            "intent_description": parsed_response.intent_description,
            "raw_extracted_data": parsed_response.extracted_data,
            "base_message": [] 
        }

        if state.get("is_first_run", True):
            update_dict["base_message"] = ["Generar saludo de bienvenida"]
            update_dict["is_first_run"] = False
        
        return update_dict
    except Exception as e:
        logger.error(f"Error al estructurar la salida del supervisor: {e}", exc_info=True)
        return {"next_node": NextNode.FALLBACK}