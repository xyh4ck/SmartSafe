from typing import Optional
from pydantic import Field

from app.core.base_schema import BaseSchema


class ModelRegistryCreateSchema(BaseSchema):
    name: str = Field(...)
    provider: str = Field(...)
    type: str = Field(...)
    api_base: Optional[str] = Field(None)
    api_key: Optional[str] = Field(None)
    available: Optional[bool] = Field(True)
    version: Optional[str] = Field(None)
    quota_limit: Optional[int] = Field(0)
    description: Optional[str] = Field(None)


class ModelRegistryUpdateSchema(BaseSchema):
    id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    provider: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    api_base: Optional[str] = Field(None)
    api_key: Optional[str] = Field(None)
    available: Optional[bool] = Field(None)
    version: Optional[str] = Field(None)
    quota_limit: Optional[int] = Field(None)
    description: Optional[str] = Field(None)


class ModelRegistryOutSchema(BaseSchema):
    id: int
    name: str
    provider: str
    type: str
    api_base: Optional[str]
    available: bool
    version: Optional[str]
    quota_limit: int
    quota_used: int
    description: Optional[str]
