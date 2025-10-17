import uuid
from .base import BaseApiClient
from ..responses.eligibility_response import EligibilityResponse
from ..requests.eligibility_request import EligibilityRequest

class EligibilityApiClient(BaseApiClient):
    """
    Cliente de API para interactuar con el endpoint de elegibilidad.
    """
    async def check_eligibility(self, client_id: uuid.UUID, vehicle_id: uuid.UUID) -> EligibilityResponse:
        """
        Llama al endpoint de la API para verificar la elegibilidad de un cliente y su vehículo.
        """
        request_data = EligibilityRequest(client_id=client_id, vehicle_id=vehicle_id)
        async with self.get_api_client() as client:
            response = await client.post("/api/eligibility/check", content=request_data.model_dump_json())
            response.raise_for_status()
            return EligibilityResponse(**response.json())