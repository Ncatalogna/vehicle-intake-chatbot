import uuid
from typing import List, Optional

from .base import BaseApiClient
from api.requests.vehicle_request import VehicleRequest
from api.responses.vehicle_response import VehicleResponse

class VehicleApiClient(BaseApiClient):
    """
    Cliente de API para interactuar con los endpoints de vehículos.
    """
    async def create_vehicle(self, vehicle_data: VehicleRequest) -> VehicleResponse:
        async with self.get_api_client() as client:
            json_data = vehicle_data.model_dump()
            json_data['client_id'] = str(json_data['client_id'])

            response = await client.post("/api/vehicles/", json=json_data)
            response.raise_for_status()
            return VehicleResponse(**response.json())

    async def get_vehicle(self, vehicle_id: uuid.UUID) -> Optional[VehicleResponse]:
        async with self.get_api_client() as client:
            response = await client.get(f"/api/vehicles/{vehicle_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return VehicleResponse(**response.json())

    async def get_client_vehicles(self, client_id: uuid.UUID) -> List[VehicleResponse]:
        async with self.get_api_client() as client:
            response = await client.get(f"/api/vehicles/client/{client_id}")
            response.raise_for_status()
            return [VehicleResponse(**item) for item in response.json()]

    async def update_vehicle(self, vehicle_id: uuid.UUID, vehicle_data: VehicleRequest) -> Optional[VehicleResponse]:
        async with self.get_api_client() as client:
            json_data = vehicle_data.model_dump()
            json_data['client_id'] = str(json_data['client_id'])

            response = await client.put(f"/api/vehicles/{vehicle_id}", json=json_data)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return VehicleResponse(**response.json())