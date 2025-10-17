import uuid
from typing import List, Dict
from langchain_core.tools import tool, BaseTool
from typing import Annotated
from pydantic import BaseModel

from api.clients.eligibility_client import EligibilityApiClient

class EligibilityResult(BaseModel):
    is_eligible: bool
    message: str
    checked_criteria: Dict[str, str]

api_client = EligibilityApiClient()

def eligibility_tool() -> List[BaseTool]:
    """
    Retorna la lista de herramientas para la evaluación de elegibilidad.
    """
    @tool(description="Evalúa si un cliente y su vehículo cumplen los criterios de elegibilidad.")
    async def check_eligibility(
        client_id: Annotated[uuid.UUID, "El ID del cliente registrado."],
        vehicle_id: Annotated[uuid.UUID, "El ID del vehículo registrado."]
    ) -> EligibilityResult:
        """
        Realiza una serie de validaciones sobre el cliente y el vehículo para determinar si son elegibles.
        """
        try:
            eligibility_response = await api_client.check_eligibility(client_id, vehicle_id)
            
            checked_criteria = {}
            if eligibility_response.reasons:
                for reason in eligibility_response.reasons:
                    if ':' in reason:
                        key, value = reason.split(':', 1)
                        checked_criteria[key.strip()] = value.strip()

            return EligibilityResult(
                is_eligible=eligibility_response.is_eligible,
                message=eligibility_response.message,
                checked_criteria=checked_criteria
            )
        except Exception as e:
            return EligibilityResult(
                is_eligible=False,
                message=f"No se pudo completar la verificación de elegibilidad debido a un error: {e}",
                checked_criteria={"error": str(e)}
            )

    return [check_eligibility]