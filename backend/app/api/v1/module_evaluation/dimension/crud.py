# -*- coding: utf-8 -*-

from typing import Optional, Dict, List, Union, Any, Sequence

from app.core.base_crud import CRUDBase
from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_evaluation.dimension.model import DimensionModel
from app.api.v1.module_evaluation.dimension.schema import DimensionCreateSchema, DimensionUpdateSchema, DimensionOutSchema


class DimensionCRUD(CRUDBase[DimensionModel, DimensionCreateSchema, DimensionUpdateSchema]):
    """维度模块数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化维度CRUD
        
        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=DimensionModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[List[Union[str, Any]]] = None) -> Optional[DimensionModel]:
        """
        根据ID获取维度信息
        
        参数:
        - id (int): 维度ID
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Optional[DimensionModel]: 维度信息，如果不存在则为None
        """
        return await self.get(
            preload=preload,
            id=id,
        )

    async def get_by_name_crud(self, name: str, preload: Optional[List[Union[str, Any]]] = None) -> Optional[DimensionModel]:
        """
        根据名称获取维度信息
        
        参数:
        - name (str): 维度名称
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Optional[DimensionModel]: 维度信息，如果不存在则为None
        """
        return await self.get(
            preload=preload,
            name=name,
        )

    async def get_by_code_crud(self, code: str, preload: Optional[List[Union[str, Any]]] = None) -> Optional[DimensionModel]:
        """
        根据代码获取维度信息
        
        参数:
        - code (str): 维度代码
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Optional[DimensionModel]: 维度信息，如果不存在则为None
        """
        return await self.get(
            preload=preload,
            code=code,
        )

    async def get_list_crud(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None, preload: Optional[List[Union[str, Any]]] = None) -> Sequence[DimensionModel]:
        """
        获取维度列表
        
        参数:
        - search (Dict | None): 查询参数对象
        - order_by (List[Dict[str, str]] | None): 排序参数列表
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，未提供时使用模型默认项
        
        返回:
        - Sequence[DimensionModel]: 维度列表
        """
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def page_list_crud(self, offset: int, limit: int, order_by: List[Dict[str, str]], search: Dict):
        """
        分页查询维度列表
        
        参数:
        - offset (int): 偏移量
        - limit (int): 每页数量
        - order_by (List[Dict[str, str]]): 排序参数列表
        - search (Dict): 查询参数对象
        
        返回:
        - 分页查询结果
        """
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=DimensionOutSchema)

    async def create_crud(self, data: DimensionCreateSchema) -> DimensionModel:
        """
        创建维度
        
        参数:
        - data (DimensionCreateSchema): 维度创建信息
        
        返回:
        - DimensionModel: 创建后的维度信息
        """
        return await self.create(data=data)

    async def update_crud(self, id: int, data: DimensionUpdateSchema) -> Optional[DimensionModel]:
        """
        更新维度
        
        参数:
        - id (int): 维度ID
        - data (DimensionUpdateSchema): 维度更新信息
        
        返回:
        - Optional[DimensionModel]: 更新后的维度信息
        """
        return await self.update(id=id, data=data)

    async def delete_crud(self, ids: List[int]) -> None:
        """
        删除维度
        
        参数:
        - ids (List[int]): 维度ID列表
        
        返回:
        - None
        """
        return await self.delete(ids=ids)

