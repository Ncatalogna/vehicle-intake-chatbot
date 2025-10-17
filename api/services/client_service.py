from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from entities.client_entity import Client
from requests.client_request import ClientRequest

class ClientService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_client(self, client_data: ClientRequest) -> Optional[Client]:
        new_client = Client(**client_data.model_dump())
        self.db_session.add(new_client)
        await self.db_session.commit()
        await self.db_session.refresh(new_client)
        
        result = await self.db_session.execute(
            select(Client).options(selectinload(Client.vehicles)).filter_by(id=new_client.id)
        )
        created_client_with_relations = result.scalars().first()
        return created_client_with_relations

    async def get_client_by_id(self, client_id: UUID) -> Optional[Client]:
        result = await self.db_session.execute(
            select(Client).options(selectinload(Client.vehicles)).filter_by(id=client_id)
        )
        return result.scalars().first()

    async def get_all_clients(self) -> List[Client]:
        result = await self.db_session.execute(
            select(Client).options(selectinload(Client.vehicles))
        )
        return list(result.scalars().all())

    async def update_client(self, client_id: UUID, update_data: ClientRequest) -> Optional[Client]:
        client = await self.get_client_by_id(client_id)
        if not client:
            return None
        
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(client, key, value)
            
        await self.db_session.commit()
        await self.db_session.refresh(client)
        
        result = await self.db_session.execute(
            select(Client).options(selectinload(Client.vehicles)).filter_by(id=client.id)
        )
        return result.scalars().first()


    async def delete_client(self, client_id: UUID) -> bool:
        client = await self.get_client_by_id(client_id)
        if client:
            await self.db_session.delete(client)
            await self.db_session.commit()
            return True
        return False