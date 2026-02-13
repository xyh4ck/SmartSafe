# -*- coding: utf-8 -*-

from typing import Optional, Dict, List, Any

from app.core.base_crud import CRUDBase
from app.api.v1.module_evaluation.testcase_candidate.model import TestCaseCandidateModel
from app.api.v1.module_evaluation.testcase_candidate.schema import TestCaseCandidateCreateSchema, TestCaseCandidateUpdateSchema


class TestCaseCandidateCRUD(CRUDBase[TestCaseCandidateModel, TestCaseCandidateCreateSchema, TestCaseCandidateUpdateSchema]):

    async def get_list_crud(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None):
        return await self.list(search=search, order_by=order_by)

    async def create_crud(self, data: Dict[str, Any]):
        return await self.create(data=data)

    async def update_crud(self, id: int, data: Dict[str, Any]):
        return await self.update(id=id, data=data)

    async def delete_crud(self, ids: List[int]):
        return await self.delete(ids=ids)

    async def batch_update_status(self, ids: List[int], status: str, reviewer_id: int, review_note: Optional[str] = None):
        """批量更新状态"""
        from datetime import datetime
        for id in ids:
            await self.update(id=id, data={
                "status": status,
                "reviewer_id": reviewer_id,
                "reviewed_at": datetime.now(),
                "review_note": review_note,
            })
