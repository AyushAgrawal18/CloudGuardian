
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class LogIn(BaseModel):
    host_id: str = Field(min_length=1, max_length=100)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    severity: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    message: str = Field(min_length=1, max_length=16384)


class LogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    host_id: str
    template_id: int
    timestamp: datetime
    severity: str
    message: str
