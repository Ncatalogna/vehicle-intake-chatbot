from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from entities.vehicle_entity import Vehicle
from requests.vehicle_request import VehicleRequest

class VehicleService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_vehicle(self, vehicle_data: VehicleRequest) -> Vehicle:
        new_vehicle = Vehicle(**vehicle_data.model_dump())
        self.db_session.add(new_vehicle)
        await self.db_session.commit()
        await self.db_session.refresh(new_vehicle)
        return new_vehicle

    async def get_vehicle_by_id(self, vehicle_id: UUID) -> Optional[Vehicle]:
        result = await self.db_session.execute(
            select(Vehicle).filter_by(id=vehicle_id)
        )
        return result.scalars().first()

    async def get_vehicles_for_client(self, client_id: UUID) -> List[Vehicle]:
        result = await self.db_session.execute(
            select(Vehicle).filter_by(client_id=client_id)
        )
        return list(result.scalars().all())