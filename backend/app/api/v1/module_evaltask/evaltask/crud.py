# -*- coding: utf-8 -*-

from typing import Optional, Sequence, List, Dict, Any, Union

from app.core.base_crud import CRUDBase
from app.api.v1.module_system.auth.schema import AuthSchema
from .model import EvalTaskModel, EvalTaskCaseModel, EvalTaskResultModel, EvalTaskLogModel
from .schema import EvalTaskCreateSchema


class EvalTaskCRUD(CRUDBase[EvalTaskModel, EvalTaskCreateSchema, EvalTaskCreateSchema]):
    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        super().__init__(model=EvalTaskModel, auth=auth)

    async def get_by_id(self, id: int) -> Optional[EvalTaskModel]:
        return await self.get(id=id)

    async def list_tasks(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None) -> Sequence[EvalTaskModel]:
        return await self.list(search=search, order_by=order_by)

    async def create_task(self, data: Dict[str, Any]) -> EvalTaskModel:
        return await self.create(data=data)

    async def update_task(self, id: int, data: Dict[str, Any]) -> EvalTaskModel:
        return await self.update(id=id, data=data)

    async def delete_tasks(self, ids: List[int]) -> int:
        """批量删除任务"""
        await self.delete(ids=ids)
        return len(ids)


class EvalTaskCaseCRUD(CRUDBase[EvalTaskCaseModel, Dict[str, Any], Dict[str, Any]]):
    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        super().__init__(model=EvalTaskCaseModel, auth=auth)

    async def list_cases(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None) -> Sequence[EvalTaskCaseModel]:
        return await self.list(search=search, order_by=order_by)

    async def create_case(self, data: Dict[str, Any]) -> EvalTaskCaseModel:
        return await self.create(data=data)

    async def update_case(self, id: int, data: Dict[str, Any]) -> EvalTaskCaseModel:
        return await self.update(id=id, data=data)


class EvalTaskResultCRUD(CRUDBase[EvalTaskResultModel, Dict[str, Any], Dict[str, Any]]):
    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        super().__init__(model=EvalTaskResultModel, auth=auth)

    async def upsert_result(self, task_id: int, summary: str, metrics: str, top_risks: str) -> EvalTaskResultModel:
        obj = await self.get(task_id=task_id)
        data = {"task_id": task_id, "summary": summary, "metrics": metrics, "top_risks": top_risks}
        if obj:
            return await self.update(id=obj.id, data=data)
        return await self.create(data=data)


class EvalTaskLogCRUD(CRUDBase[EvalTaskLogModel, Dict[str, Any], Dict[str, Any]]):
    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        super().__init__(model=EvalTaskLogModel, auth=auth)

    async def write_log(self, task_id: int, stage: str, message: str, level: str = "INFO", case_id: Optional[int] = None) -> EvalTaskLogModel:
        return await self.create({
            "task_id": task_id,
            "case_id": case_id,
            "stage": stage,
            "message": message,
            "level": level
        })