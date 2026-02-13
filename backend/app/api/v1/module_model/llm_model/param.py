from typing import Optional
from fastapi import Query


class ModelRegistryQueryParam:
    def __init__(
        self,
        name: Optional[str] = Query(None),
        provider: Optional[str] = Query(None),
        type: Optional[int] = Query(None),
        available: Optional[bool] = Query(None),
    ) -> None:
        self.name = ("like", name) if name else None
        self.provider = provider
        self.type = type
        self.available = available