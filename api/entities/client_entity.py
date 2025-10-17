import uuid
import enum
from datetime import date
from typing import List, TYPE_CHECKING
from sqlalchemy import Date, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import UUID

from .base_entity import BaseEntity

if TYPE_CHECKING:
    from .vehicle_entity import Vehicle

class IdentificationType(enum.Enum):
    DNI = "dni"
    CUIT = "cuit"
    CUIL = "cuil"

class Client(BaseEntity):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    documento: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    documento_type: Mapped[IdentificationType] = mapped_column(SQLAlchemyEnum(IdentificationType), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)

    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="client", cascade="all, delete-orphan")