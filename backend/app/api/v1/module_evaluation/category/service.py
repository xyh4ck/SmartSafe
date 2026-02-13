# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_

from app.api.v1.module_evaluation.category.model import CategoryModel
from app.api.v1.module_evaluation.category.schema import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryOutSchema,
    CategoryWithDimensionSchema
)
from app.api.v1.module_evaluation.category.crud import CategoryCRUD
from app.core.exceptions import CustomException


class CategoryService:
    def __init__(self, crud: CategoryCRUD) -> None:
        self.crud = crud
        self.db = crud.db

    async def _ensure_unique(self, data: dict, exclude_id: Optional[int] = None) -> None:
        """检查同一维度下名称或代码的唯一性"""
        conditions = []
        
        # 同一维度下的名称唯一性检查
        if "name" in data and "dimension_id" in data:
            name_condition = and_(
                CategoryModel.name == data.get("name"),
                CategoryModel.dimension_id == data.get("dimension_id")
            )
            conditions.append(name_condition)
        
        # 同一维度下的代码唯一性检查（如果提供了代码）
        if data.get("code") and "dimension_id" in data:
            code_condition = and_(
                CategoryModel.code == data.get("code"),
                CategoryModel.dimension_id == data.get("dimension_id")
            )
            conditions.append(code_condition)
        
        if conditions:
            from sqlalchemy import or_
            sql = select(CategoryModel).where(or_(*conditions))
            if exclude_id:
                sql = sql.where(CategoryModel.id != exclude_id)
            existing = await self.db.scalar(sql)
            if existing:
                if existing.name == data.get("name"):
                    raise CustomException(msg=f"该维度下分类名称 '{data.get('name')}' 已存在")
                if existing.code == data.get("code"):
                    raise CustomException(msg=f"该维度下分类代码 '{data.get('code')}' 已存在")

    async def create(self, data: CategoryCreateSchema) -> Dict[str, Any]:
        payload = data.model_dump()
        await self._ensure_unique(payload)
        obj = await self.crud.create_crud(data=CategoryCreateSchema(**payload))
        return CategoryOutSchema.model_validate(obj).model_dump()

    async def update(self, id: int, data: CategoryUpdateSchema) -> Dict[str, Any]:
        payload = data.model_dump(exclude_unset=True, exclude={"id"})
        await self._ensure_unique(payload, exclude_id=id)
        obj = await self.crud.update_crud(id=id, data=CategoryUpdateSchema(**payload))
        return CategoryOutSchema.model_validate(obj).model_dump()

    async def delete(self, ids: List[int]) -> None:
        """删除分类前检查是否有测试用例在使用"""
        from app.api.v1.module_evaluation.testcase.model import TestCaseModel
        
        for cat_id in ids:
            # 检查该分类下是否有测试用例
            sql = select(TestCaseModel).where(TestCaseModel.category_id == cat_id)
            testcases = await self.db.scalars(sql)
            if testcases.first():
                cat = await self.crud.get(id=cat_id)
                cat_name = cat.name if cat else f"ID:{cat_id}"
                raise CustomException(msg=f"分类 '{cat_name}' 下存在测试用例，无法删除")
        
        await self.crud.delete_crud(ids=ids)

    async def list(self, search: Optional[Dict] = None, order_by: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
        """获取分类列表，默认按排序字段升序"""
        if order_by is None:
            order_by = [{"sort": "asc"}, {"id": "asc"}]
        rows = await self.crud.get_list_crud(search=search, order_by=order_by, preload=["dimension"])
        return [CategoryWithDimensionSchema.model_validate(r).model_dump() for r in rows]

    async def get_by_dimension(self, dimension_id: int, only_active: bool = False) -> List[Dict[str, Any]]:
        """根据维度ID获取分类列表"""
        search = {"dimension_id": dimension_id}
        if only_active:
            search["status"] = True
        order_by = [{"sort": "asc"}, {"id": "asc"}]
        rows = await self.crud.get_list_crud(search=search, order_by=order_by)
        return [CategoryOutSchema.model_validate(r).model_dump() for r in rows]

    async def get_dimension_category_tree(self, only_active: bool = False) -> List[Dict[str, Any]]:
        """
        一次性获取所有维度及其分类的树形结构
        优化性能：使用单次查询 + 内存分组，避免 N+1 查询问题
        """
        from app.api.v1.module_evaluation.dimension.model import DimensionModel
        from collections import defaultdict
        
        # 1. 查询所有启用的维度
        dimension_search = {"status": True} if only_active else {}
        dimension_sql = select(DimensionModel)
        if dimension_search:
            for key, value in dimension_search.items():
                dimension_sql = dimension_sql.where(getattr(DimensionModel, key) == value)
        dimension_sql = dimension_sql.order_by(DimensionModel.sort, DimensionModel.id)
        dimensions = await self.db.scalars(dimension_sql)
        dimension_list = list(dimensions)
        
        # 2. 一次性查询所有分类（根据需要过滤启用状态）
        category_search = {}
        if only_active:
            category_search["status"] = True
        order_by = [{"sort": "asc"}, {"id": "asc"}]
        all_categories = await self.crud.get_list_crud(search=category_search, order_by=order_by)
        
        # 3. 按维度ID分组分类
        categories_by_dimension = defaultdict(list)
        for cat in all_categories:
            cat_dict = CategoryOutSchema.model_validate(cat).model_dump()
            categories_by_dimension[cat_dict["dimension_id"]].append(cat_dict)
        
        # 4. 构建树形结构
        tree = []
        for dim in dimension_list:
            tree.append({
                "dimension_id": dim.id,
                "dimension_name": dim.name,
                "dimension_code": dim.code,
                "dimension_status": dim.status,
                "categories": categories_by_dimension.get(dim.id, [])
            })
        
        return tree

