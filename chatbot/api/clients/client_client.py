import uuid
from typing import List, Optional

from api.clients.base import BaseApiClient
from api.requests.client_request import ClientRequest
from api.responses.client_response import ClientResponse

class ClientApiClient(BaseApiClient):
    """
    Cliente de API para interactuar con los endpoints de clientes.
    """
    async def create_client(self, client_data: ClientRequest) -> ClientResponse:
        async with self.get_api_client() as client:
            json_data = client_data.model_dump(by_alias=True)
            if json_data.get("birth_date"):
                json_data["birth_date"] = json_data["birth_date"].isoformat()
            if json_data.get("documento_type"):
                json_data["documento_type"] = json_data["documento_type"].value

            response = await client.post("/api/clients/", json=json_data)
            response.raise_for_status()
            return ClientResponse(**response.json())

    async def get_client(self, client_id: uuid.UUID) -> Optional[ClientResponse]:
        async with self.get_api_client() as client:
            response = await client.get(f"/api/clients/{client_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return ClientResponse(**response.json())

    async def get_all_clients(self) -> List[ClientResponse]:
        async with self.get_api_client() as client:
            response = await client.get("/api/clients/")
            response.raise_for_status()
            return [ClientResponse(**item) for item in response.json()]

    async def update_client(self, client_id: uuid.UUID, client_data: ClientRequest) -> Optional[ClientResponse]:
        async with self.get_api_client() as client:
            json_data = client_data.model_dump(by_alias=True)
            if json_data.get("birth_date"):
                json_data["birth_date"] = json_data["birth_date"].isoformat()
            if json_data.get("documento_type"):
                json_data["documento_type"] = json_data["documento_type"].value

            response = await client.put(f"/api/clients/{client_id}", json=json_data)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return ClientResponse(**response.json())

    async def delete_client(self, client_id: uuid.UUID) -> bool:
        async with self.get_api_client() as client:
            response = await client.delete(f"/api/clients/{client_id}")
            if response.status_code == 404:
                return False
            response.raise_for_status()
            return True