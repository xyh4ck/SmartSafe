# -*- coding: utf-8 -*-

from typing import Optional, Dict, List, Union, Any

from app.core.base_crud import CRUDBase
from app.api.v1.module_evaluation.keyword_questionbank.model import KeywordModel
from app.api.v1.module_evaluation.keyword_questionbank.schema import (
    KeywordCreateSchema, KeywordUpdateSchema
)


class KeywordCRUD(CRUDBase[KeywordModel, KeywordCreateSchema, KeywordUpdateSchema]):
    """关键词 CRUD"""

    async def get_list_crud(
        self, 
        search: Optional[Dict] = None, 
        order_by: Optional[List[Dict[str, str]]] = None,
        preload: Optional[List[Union[str, Any]]] = None
    ):
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def page_list_crud(
        self, 
        offset: int, 
        limit: int, 
        order_by: List[Dict[str, str]], 
        search: Dict
    ):
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=None)

    async def create_crud(self, data: KeywordCreateSchema):
        return await self.create(data=data)

    async def update_crud(self, id: int, data: KeywordUpdateSchema):
        return await self.update(id=id, data=data)

    async def delete_crud(self, ids: List[int]):
        return await self.delete(ids=ids)

    async def get_by_word_and_category(self, word: str, category_id: int) -> Optional[KeywordModel]:
        """根据关键词和类别获取"""
        from sqlalchemy import select, and_
        sql = select(KeywordModel).where(
            and_(
                KeywordModel.word == word,
                KeywordModel.category_id == category_id
            )
        )
        return await self.db.scalar(sql)

    async def get_by_category(self, category_id: int, status: Optional[bool] = None) -> List[KeywordModel]:
        """获取某类别下的所有关键词"""
        from sqlalchemy import select, and_
        conditions = [KeywordModel.category_id == category_id]
        if status is not None:
            conditions.append(KeywordModel.status == status)
        sql = select(KeywordModel).where(and_(*conditions))
        result = await self.db.scalars(sql)
        return list(result.all())

    async def get_all_active(self) -> List[KeywordModel]:
        """获取所有启用的关键词"""
        from sqlalchemy import select
        sql = select(KeywordModel).where(KeywordModel.status == True)
        result = await self.db.scalars(sql)
        return list(result.all())

    async def increment_hit_count(self, keyword_ids: List[int]) -> None:
        """增加命中次数"""
        from sqlalchemy import update
        if not keyword_ids:
            return
        stmt = update(KeywordModel).where(
            KeywordModel.id.in_(keyword_ids)
        ).values(hit_count=KeywordModel.hit_count + 1)
        await self.db.execute(stmt)
        await self.db.flush()
