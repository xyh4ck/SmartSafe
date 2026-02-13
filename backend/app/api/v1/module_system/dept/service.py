# -*- coding: utf-8 -*-

from typing import List, Dict, Optional

from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.utils.common_util import (
    get_parent_id_map,
    get_parent_recursion,
    get_child_id_map,
    get_child_recursion,
    traversal_to_tree
)
from ..auth.schema import AuthSchema
from .crud import DeptCRUD
from .param import DeptQueryParam
from .schema import (
    DeptCreateSchema,
    DeptUpdateSchema,
    DeptOutSchema
)


class DeptService:
    """
    部门管理模块服务层
    """

    @classmethod
    async def get_dept_detail_service(cls, auth: AuthSchema, id: int) -> Dict:
        """
        获取部门详情。
        
        参数:
        - auth (AuthSchema): 认证对象。
        - id (int): 部门 ID。
        
        返回:
        - Dict: 部门详情对象。
        """
        dept = await DeptCRUD(auth).get_by_id_crud(id=id)
        if dept and dept.parent_id:
            parent = await DeptCRUD(auth).get(id=dept.parent_id)
            if parent:
                DeptOutSchema.parent_name = parent.name
        return DeptOutSchema.model_validate(dept).model_dump()

    @classmethod
    async def get_dept_tree_service(cls, auth: AuthSchema, search: Optional[DeptQueryParam]= None, order_by: Optional[List[Dict]] = None) -> List[Dict]:
        """
        获取部门树形列表。
        
        参数:
        - auth (AuthSchema): 认证对象。
        - search (DeptQueryParam | None): 查询参数对象。
        - order_by (List[Dict] | None): 排序参数。
        
        返回:
        - List[Dict]: 部门树形列表对象。
        """
        # 使用树形结构查询，预加载children关系
        dept_list = await DeptCRUD(auth).get_tree_list_crud(search=search.__dict__, order_by=order_by)
        # 转换为字典列表
        dept_dict_list = [DeptOutSchema.model_validate(dept).model_dump() for dept in dept_list]
        # 使用traversal_to_tree构建树形结构
        return traversal_to_tree(dept_dict_list)

    @classmethod
    async def create_dept_service(cls, auth: AuthSchema, data: DeptCreateSchema) -> Dict:
        """
        创建部门。
        
        参数:
        - auth (AuthSchema): 认证对象。
        - data (DeptCreateSchema): 部门创建对象。
        
        返回:
        - Dict: 新创建的部门对象。
        
        异常:
        - CustomException: 当部门已存在时抛出。
        """
        dept = await DeptCRUD(auth).get(name=data.name)
        if dept:
            raise CustomException(msg='创建失败，该部门已存在')
        dept = await DeptCRUD(auth).create(data=data)
        return DeptOutSchema.model_validate(dept).model_dump()

    @classmethod
    async def update_dept_service(cls, auth: AuthSchema, id:int, data: DeptUpdateSchema) -> Dict:
        """
        更新部门。
        
        参数:
        - auth (AuthSchema): 认证对象。
        - id (int): 部门 ID。
        - data (DeptUpdateSchema): 部门更新对象。
        
        返回:
        - Dict: 更新后的部门对象。
        
        异常:
        - CustomException: 当部门不存在或名称重复时抛出。
        """
        dept = await DeptCRUD(auth).get_by_id_crud(id=id)
        if not dept:
            raise CustomException(msg='更新失败，该部门不存在')
        exist_dept = await DeptCRUD(auth).get(name=data.name)
        if exist_dept and exist_dept.id != id:
            raise CustomException(msg='更新失败，部门名称重复')
        dept = await DeptCRUD(auth).update(id=id, data=data)
        if data.status:
            await cls.batch_set_available_service(auth=auth, data=BatchSetAvailable(ids=[id], status=True))
        else:
            await cls.batch_set_available_service(auth=auth, data=BatchSetAvailable(ids=[id], status=False))
        return DeptOutSchema.model_validate(dept).model_dump()

    @classmethod
    async def delete_dept_service(cls, auth: AuthSchema, ids: list[int]) -> None:
        """
        删除部门。
        
        参数:
        - auth (AuthSchema): 认证对象。
        - ids (List[int]): 部门 ID 列表。
        
        返回:
        - None
        
        异常:
        - CustomException: 当删除对象为空或部门不存在时抛出。
        """
        if len(ids) < 1:
            raise CustomException(msg='删除失败，删除对象不能为空')
        for id in ids:
            dept = await DeptCRUD(auth).get_by_id_crud(id=id)
            if not dept:
                raise CustomException(msg='删除失败，该部门不存在')
        # 校验是否存在子级部门，存在则禁止删除
        dept_list = await DeptCRUD(auth).get_list_crud()
        id_map = get_child_id_map(model_list=dept_list)
        for id in ids:
            descendants = get_child_recursion(id=id, id_map=id_map)
            if len(descendants) > 1:
                raise CustomException(msg='删除失败，存在子级部门，请先删除子级部门')
        await DeptCRUD(auth).delete(ids=ids)

    @classmethod
    async def batch_set_available_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
        """
        批量设置部门可用状态。
        
        参数:
        - auth (AuthSchema): 认证对象。
        - data (BatchSetAvailable): 批量设置可用状态对象。
        
        返回:
        - None
        """
        dept_list = await DeptCRUD(auth).get_list_crud()
        total_ids = []
        
        if data.status:
            id_map = get_parent_id_map(model_list=dept_list)
            for dept_id in data.ids:
                enable_ids = get_parent_recursion(id=dept_id, id_map=id_map)
                total_ids.extend(enable_ids)
        else:
            id_map = get_child_id_map(model_list=dept_list)
            for dept_id in data.ids:
                disable_ids = get_child_recursion(id=dept_id, id_map=id_map)
                total_ids.extend(disable_ids)

        await DeptCRUD(auth).set_available_crud(ids=total_ids, status=data.status)