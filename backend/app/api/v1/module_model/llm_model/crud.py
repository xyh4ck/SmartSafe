from typing import Optional, Sequence, List, Dict, Any

from app.core.base_crud import CRUDBase
from app.api.v1.module_system.auth.schema import AuthSchema
from .model import ModelRegistryModel
from .schema import ModelRegistryCreateSchema, ModelRegistryUpdateSchema


class ModelRegistryCRUD(CRUDBase[ModelRegistryModel, ModelRegistryCreateSchema, ModelRegistryUpdateSchema]):
    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(ModelRegistryModel, auth)

    async def get_by_id_crud(self, id: int) -> Optional[ModelRegistryModel]:
        return await self.get(id=id)

    async def get_list_crud(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None) -> Sequence[ModelRegistryModel]:
        return await self.list(search=search, order_by=order_by)