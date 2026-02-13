# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Sequence, Union, Any

from app.core.base_crud import CRUDBase
from ..auth.schema import AuthSchema
from .model import ParamsModel
from .schema import ParamsCreateSchema, ParamsUpdateSchema


class ParamsCRUD(CRUDBase[ParamsModel, ParamsCreateSchema, ParamsUpdateSchema]):
    """配置管理数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化配置CRUD
        
        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=ParamsModel, auth=auth)
    
    async def get_obj_by_id_crud(self, id: int, preload: Optional[List[Union[str, Any]]] = None) -> Optional[ParamsModel]:
        """
        获取配置管理型详情
        
        参数:
        - id (int): 配置管理型ID
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Optional[ParamsModel]: 配置管理型模型实例
        """
        return await self.get(id=id, preload=preload)
    
    async def get_obj_by_key_crud(self, key: str, preload: Optional[List[Union[str, Any]]] = None) -> Optional[ParamsModel]:
        """
        根据key获取配置管理型详情
        
        参数:
        - key (str): 配置管理型key
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Optional[ParamsModel]: 配置管理型模型实例
        """
        return await self.get(config_key=key, preload=preload)
    
    async def get_obj_list_crud(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None, preload: Optional[List[Union[str, Any]]] = None) -> Sequence[ParamsModel]:
        """
        获取配置管理型列表
        
        参数:
        - search (Dict | None): 查询参数对象。
        - order_by (List[Dict[str, str]] | None): 排序参数列表。
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Sequence[ParamsModel]: 配置管理型模型实例列表
        """
        return await self.list(search=search, order_by=order_by, preload=preload)
    
    async def create_obj_crud(self, data: ParamsCreateSchema) -> Optional[ParamsModel]:
        """
        创建配置管理型
        
        参数:
        - data (ParamsCreateSchema): 创建配置管理型负载模型
        
        返回:
        - Optional[ParamsModel]: 配置管理型模型实例
        """
        return await self.create(data=data)
    
    async def update_obj_crud(self, id: int, data: ParamsUpdateSchema) -> Optional[ParamsModel]:
        """
        更新配置管理型
        
        参数:
        - id (int): 配置管理型ID
        - data (ParamsUpdateSchema): 更新配置管理型负载模型
        
        返回:
        - Optional[ParamsModel]: 配置管理型模型实例
        """
        return await self.update(id=id, data=data)
    
    async def delete_obj_crud(self, ids: List[int]) -> None:
        """
        删除配置管理型
        
        参数:
        - ids (List[int]): 配置管理型ID列表
        
        返回:
        - None
        """
        return await self.delete(ids=ids)