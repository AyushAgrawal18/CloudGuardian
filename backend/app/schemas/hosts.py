
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress

from backend.app.models.host import HostStatus


class HostCreate(BaseModel):
    host_id: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=150)
    hostname: str = Field(min_length=1, max_length=255)
    ip_address: IPvAnyAddress
    environment: str = Field(min_length=2, max_length=50)
    operating_system: str = Field(min_length=2, max_length=100)


class HostUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    hostname: str | None = Field(default=None, min_length=1, max_length=255)
    ip_address: IPvAnyAddress | None = None
    environment: str | None = Field(default=None, min_length=2, max_length=50)
    operating_system: str | None = Field(default=None, min_length=2, max_length=100)
    status: HostStatus | None = None


class HostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    host_id: str
    name: str
    hostname: str
    ip_address: str
    environment: str
    operating_system: str
    status: HostStatus
    created_at: datetime
    updated_at: datetime
