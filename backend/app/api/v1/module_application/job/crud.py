# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Sequence, Union, Any

from app.core.base_crud import CRUDBase
from app.api.v1.module_system.auth.schema import AuthSchema
from .model import JobModel, JobLogModel
from .schema import JobCreateSchema,JobUpdateSchema,JobLogCreateSchema,JobLogUpdateSchema


class JobCRUD(CRUDBase[JobModel, JobCreateSchema, JobUpdateSchema]):
    """定时任务数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化定时任务CRUD
        
        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=JobModel, auth=auth)

    async def get_obj_by_id_crud(self, id: int, preload: Optional[List[Union[str, Any]]] = None) -> Optional[JobModel]:
        """
        获取定时任务详情
        
        参数:
        - id (int): 定时任务ID
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Optional[JobModel]: 定时任务模型,如果不存在则为None
        """
        return await self.get(id=id, preload=preload)
    
    async def get_obj_list_crud(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None, preload: Optional[List[Union[str, Any]]] = None) -> Sequence[JobModel]:
        """
        获取定时任务列表
        
        参数:
        - search (Optional[Dict]): 查询参数字典
        - order_by (Optional[List[Dict[str, str]]]): 排序参数列表
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Sequence[JobModel]: 定时任务模型序列
        """
        return await self.list(search=search, order_by=order_by, preload=preload)
    
    async def create_obj_crud(self, data: JobCreateSchema) -> Optional[JobModel]:
        """
        创建定时任务
        
        参数:
        - data (JobCreateSchema): 创建定时任务模型
        
        返回:
        - Optional[JobModel]: 创建的定时任务模型,如果创建失败则为None
        """
        return await self.create(data=data)
    
    async def update_obj_crud(self, id: int, data: JobUpdateSchema) -> Optional[JobModel]:
        """
        更新定时任务
        
        参数:
        - id (int): 定时任务ID
        - data (JobUpdateSchema): 更新定时任务模型
        
        返回:
        - Optional[JobModel]: 更新后的定时任务模型,如果更新失败则为None
        """
        return await self.update(id=id, data=data)
    
    async def delete_obj_crud(self, ids: List[int]) -> None:
        """
        删除定时任务
        
        参数:
        - ids (List[int]): 定时任务ID列表
        """
        return await self.delete(ids=ids)
    
    async def set_obj_field_crud(self, ids: List[int], **kwargs) -> None:
        """
        设置定时任务的可用状态
        
        参数:
        - ids (List[int]): 定时任务ID列表
        - kwargs: 其他要设置的字段,例如 available=True 或 available=False
        """
        return await self.set(ids=ids, **kwargs)
    
    async def clear_obj_crud(self) -> None:
        """
        清除定时任务日志
        
        注意:
        - 此操作会删除所有定时任务日志,请谨慎操作
        """
        return await self.clear()


class JobLogCRUD(CRUDBase[JobLogModel, JobLogCreateSchema, JobLogUpdateSchema]):
    """定时任务日志数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化定时任务日志CRUD
        
        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=JobLogModel, auth=auth)

    async def get_obj_log_by_id_crud(self, id: int, preload: Optional[List[Union[str, Any]]] = None) -> Optional[JobLogModel]:
        """
        获取定时任务日志详情
        
        参数:
        - id (int): 定时任务日志ID
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Optional[JobLogModel]: 定时任务日志模型,如果不存在则为None
        """
        return await self.get(id=id, preload=preload)
    
    async def get_obj_log_list_crud(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None, preload: Optional[List[Union[str, Any]]] = None) -> Sequence[JobLogModel]:
        """
        获取定时任务日志列表
        
        参数:
        - search (Optional[Dict]): 查询参数字典
        - order_by (Optional[List[Dict[str, str]]]): 排序参数列表
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Sequence[JobLogModel]: 定时任务日志模型序列
        """
        return await self.list(search=search, order_by=order_by, preload=preload)
    
    async def delete_obj_log_crud(self, ids: List[int]) -> None:
        """
        删除定时任务日志
        
        参数:
        - ids (List[int]): 定时任务日志ID列表
        """
        return await self.delete(ids=ids)
    
    async def clear_obj_log_crud(self) -> None:
        """
        清除定时任务日志
        
        注意:
        - 此操作会删除所有定时任务日志,请谨慎操作
        """
        return await self.clear()