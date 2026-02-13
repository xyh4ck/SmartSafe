# -*- coding: utf-8 -*-

from typing import Optional, Dict, List, Union, Any

from app.core.base_crud import CRUDBase
from app.api.v1.module_evaluation.category.model import CategoryModel
from app.api.v1.module_evaluation.category.schema import CategoryCreateSchema, CategoryUpdateSchema


class CategoryCRUD(CRUDBase[CategoryModel, CategoryCreateSchema, CategoryUpdateSchema]):

    async def get_list_crud(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None, preload: Optional[List[Union[str, Any]]] = None):
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def page_list_crud(self, offset: int, limit: int, order_by: List[Dict[str, str]], search: Dict):
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=None)

    async def create_crud(self, data: CategoryCreateSchema):
        return await self.create(data=data)

    async def update_crud(self, id: int, data: CategoryUpdateSchema):
        return await self.update(id=id, data=data)

    async def delete_crud(self, ids: List[int]):
        return await self.delete(ids=ids)

