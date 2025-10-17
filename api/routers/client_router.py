from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.client_service import ClientService
from requests.client_request import ClientRequest
from responses.client_response import ClientResponse

router = APIRouter(prefix="/clients", tags=["Clients"])

def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
    return ClientService(db)

@router.post("/", response_model=ClientResponse, status_code=201)
async def create_client(
    client_data: ClientRequest,
    service: ClientService = Depends(get_client_service)
):
    return await service.create_client(client_data)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID, service: ClientService = Depends(get_client_service)
):
    client = await service.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/", response_model=List[ClientResponse])
async def get_all_clients(service: ClientService = Depends(get_client_service)):
    return await service.get_all_clients()

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientRequest,
    service: ClientService = Depends(get_client_service),
):
    updated = await service.update_client(client_id, client_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated

@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: UUID, service: ClientService = Depends(get_client_service)
):
    if not await service.delete_client(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    return {}