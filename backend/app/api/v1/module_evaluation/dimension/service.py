# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
from sqlalchemy import select

from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_evaluation.dimension.schema import (
    DimensionCreateSchema,
    DimensionUpdateSchema,
    DimensionOutSchema,
    DimensionWithCategoriesSchema
)
from app.api.v1.module_evaluation.dimension.crud import DimensionCRUD
from app.core.exceptions import CustomException


class DimensionService:
    """维度模块服务层"""

    @classmethod
    async def get_detail_by_id_service(cls, auth: AuthSchema, id: int) -> Dict:
        """
        根据ID获取维度详情
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - id (int): 维度ID
        
        返回:
        - Dict: 维度详情字典
        """
        dimension = await DimensionCRUD(auth).get_by_id_crud(id=id, preload=["categories"])
        if not dimension:
            raise CustomException(msg="维度不存在")
        return DimensionWithCategoriesSchema.model_validate(dimension).model_dump()

    @classmethod
    async def get_dimension_list_service(cls, auth: AuthSchema, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None) -> List[Dict]:
        """
        获取维度列表
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - search (Dict | None): 查询参数对象
        - order_by (List[Dict[str, str]] | None): 排序参数列表
        
        返回:
        - List[Dict]: 维度详情字典列表
        """
        if order_by is None:
            order_by = [{"sort": "asc"}, {"id": "asc"}]
        dimension_list = await DimensionCRUD(auth).get_list_crud(search=search, order_by=order_by, preload=["categories"])
        return [DimensionWithCategoriesSchema.model_validate(dimension).model_dump() for dimension in dimension_list]

    @classmethod
    async def get_dimension_page_service(
        cls,
        auth: AuthSchema,
        page_no: int,
        page_size: int,
        search: Optional[Dict] = None,
        order_by: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        """获取维度分页数据（DB 层分页，避免全量查询后内存分页导致的性能问题）"""
        if order_by is None:
            order_by = [{"sort": "asc"}, {"id": "asc"}]
        offset = (page_no - 1) * page_size
        return await DimensionCRUD(auth).page(
            offset=offset,
            limit=page_size,
            order_by=order_by,
            search=search or {},
            out_schema=DimensionWithCategoriesSchema,
            preload=["categories"],
        )

    @classmethod
    async def create_dimension_service(cls, auth: AuthSchema, data: DimensionCreateSchema) -> Dict:
        """
        创建维度
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - data (DimensionCreateSchema): 维度创建信息
        
        返回:
        - Dict: 创建后的维度详情字典
        """
        # 检查名称是否为空
        if not data.name:
            raise CustomException(msg="维度名称不能为空")
        
        # 检查名称唯一性
        existing_dimension = await DimensionCRUD(auth).get_by_name_crud(name=data.name)
        if existing_dimension:
            raise CustomException(msg=f"维度名称 '{data.name}' 已存在")
        
        # 检查代码唯一性（如果提供了代码）
        if data.code:
            existing_code = await DimensionCRUD(auth).get_by_code_crud(code=data.code)
            if existing_code:
                raise CustomException(msg=f"维度代码 '{data.code}' 已存在")
        
        # 创建维度
        new_dimension = await DimensionCRUD(auth).create_crud(data=data)
        return DimensionOutSchema.model_validate(new_dimension).model_dump()

    @classmethod
    async def update_dimension_service(cls, auth: AuthSchema, id: int, data: DimensionUpdateSchema) -> Dict:
        """
        更新维度
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - id (int): 维度ID
        - data (DimensionUpdateSchema): 维度更新信息
        
        返回:
        - Dict: 更新后的维度详情字典
        """
        # 检查维度是否存在
        dimension = await DimensionCRUD(auth).get_by_id_crud(id=id)
        if not dimension:
            raise CustomException(msg="维度不存在")
        
        # 检查名称是否为空
        if data.name and not data.name.strip():
            raise CustomException(msg="维度名称不能为空")
        
        # 检查名称唯一性
        if data.name:
            existing_dimension = await DimensionCRUD(auth).get_by_name_crud(name=data.name)
            if existing_dimension and existing_dimension.id != id:
                raise CustomException(msg=f"维度名称 '{data.name}' 已存在")
        
        # 检查代码唯一性（如果提供了代码）
        if data.code:
            existing_code = await DimensionCRUD(auth).get_by_code_crud(code=data.code)
            if existing_code and existing_code.id != id:
                raise CustomException(msg=f"维度代码 '{data.code}' 已存在")
        
        # 更新维度
        payload = data.model_dump(exclude_unset=True, exclude={"id"})
        updated_dimension = await DimensionCRUD(auth).update_crud(id=id, data=DimensionUpdateSchema(**payload))
        return DimensionOutSchema.model_validate(updated_dimension).model_dump()

    @classmethod
    async def delete_dimension_service(cls, auth: AuthSchema, ids: List[int]) -> None:
        """
        删除维度
        
        参数:
        - auth (AuthSchema): 认证信息模型
        - ids (List[int]): 维度ID列表
        
        返回:
        - None
        """
        if len(ids) < 1:
            raise CustomException(msg="删除失败，删除对象不能为空")
        
        from app.api.v1.module_evaluation.category.model import CategoryModel
        
        for dim_id in ids:
            # 检查维度是否存在
            dimension = await DimensionCRUD(auth).get_by_id_crud(id=dim_id)
            if not dimension:
                raise CustomException(msg=f"维度ID {dim_id} 不存在")
            
            # 检查该维度下是否有分类
            crud = DimensionCRUD(auth)
            sql = select(CategoryModel).where(CategoryModel.dimension_id == dim_id)
            categories = await crud.db.scalars(sql)
            if categories.first():
                raise CustomException(msg=f"维度 '{dimension.name}' 下存在分类，无法删除")
        
        # 删除维度
        await DimensionCRUD(auth).delete_crud(ids=ids)

    @classmethod
    async def get_all_active_dimension_service(cls, auth: AuthSchema) -> List[Dict]:
        """
        获取所有启用的维度（用于下拉选择）
        
        参数:
        - auth (AuthSchema): 认证信息模型
        
        返回:
        - List[Dict]: 启用的维度详情字典列表
        """
        search = {"status": True}
        order_by = [{"sort": "asc"}, {"id": "asc"}]
        dimension_list = await DimensionCRUD(auth).get_list_crud(search=search, order_by=order_by, preload=["categories"])
        return [DimensionWithCategoriesSchema.model_validate(dimension).model_dump() for dimension in dimension_list]

