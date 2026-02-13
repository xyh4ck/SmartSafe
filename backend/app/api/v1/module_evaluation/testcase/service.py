# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
from sqlalchemy import select

from app.api.v1.module_evaluation.testcase.model import TestCaseModel, TestCaseVersionModel
from app.api.v1.module_evaluation.testcase.schema import TestCaseCreateSchema, TestCaseUpdateSchema, TestCaseOutSchema
from app.api.v1.module_evaluation.testcase.crud import TestCaseCRUD
from app.core.exceptions import CustomException
from app.utils.excel_util import ExcelUtil


class TestCaseService:
    def __init__(self, crud: TestCaseCRUD) -> None:
        self.crud = crud
        self.db = crud.db

    async def _ensure_unique(self, data: dict) -> None:
        # 重复校验：同一维度+分类下相同prompt则判定重复
        from sqlalchemy import and_
        sql = select(TestCaseModel).where(
            and_(
                TestCaseModel.dimension_id == data.get("dimension_id"),
                TestCaseModel.category_id == data.get("category_id"),
                TestCaseModel.prompt == data.get("prompt"),
            )
        )
        if await self.db.scalar(sql):
            raise CustomException(msg="存在重复用例：相同维度/分类下的相同提示")

    async def create(self, data: TestCaseCreateSchema) -> Dict[str, Any]:
        payload = data.model_dump()
        # 验证维度和分类是否存在且匹配，获取对象用于自动填充
        dimension, category = await self._validate_dimension_and_category(payload.get("dimension_id"), payload.get("category_id"))
        # 自动填充 category 和 subcategory（如果未提供）
        if not payload.get("category"):
            payload["category"] = dimension.name
        if not payload.get("subcategory"):
            payload["subcategory"] = category.name
        # JSON字段规范化
        if payload.get("tags") is not None:
            payload["tags"] = {"items": payload["tags"]}
        await self._ensure_unique(payload)
        obj = await self.crud.create_crud(data=TestCaseCreateSchema(**payload))
        # 记录版本快照
        await self._create_version_snapshot(obj)
        # 返回 Pydantic 输出，避免直接返回 ORM
        return TestCaseOutSchema.model_validate(obj).model_dump()
    
    async def _validate_dimension_and_category(self, dimension_id: int, category_id: int):
        """验证维度和分类是否存在且匹配，返回维度对象和分类对象"""
        from app.api.v1.module_evaluation.dimension.model import DimensionModel
        from app.api.v1.module_evaluation.category.model import CategoryModel
        from sqlalchemy import and_
        
        # 验证维度是否存在
        dimension = await self.db.scalar(select(DimensionModel).where(DimensionModel.id == dimension_id))
        if not dimension:
            raise CustomException(msg=f"维度ID {dimension_id} 不存在")
        if not dimension.status:
            raise CustomException(msg=f"维度 '{dimension.name}' 未启用")
        
        # 验证分类是否存在且属于该维度
        category = await self.db.scalar(
            select(CategoryModel).where(
                and_(
                    CategoryModel.id == category_id,
                    CategoryModel.dimension_id == dimension_id
                )
            )
        )
        if not category:
            raise CustomException(msg=f"分类ID {category_id} 不存在或不属于维度ID {dimension_id}")
        if not category.status:
            raise CustomException(msg=f"分类 '{category.name}' 未启用")
        
        return dimension, category

    async def update(self, id: int, data: TestCaseUpdateSchema) -> Dict[str, Any]:
        # 读取旧对象
        obj = await self.crud.get(id=id)
        if not obj:
            raise CustomException(msg="用例不存在")
        payload = data.model_dump(exclude_unset=True, exclude={"id"})
        if payload.get("tags") is not None:
            payload["tags"] = {"items": payload["tags"]}
        # bump 版本
        payload["version"] = (obj.version or 1) + 1
        # 验证维度和分类（如果修改了），并自动填充 category 和 subcategory
        if "dimension_id" in payload or "category_id" in payload:
            dim_id = payload.get("dimension_id", obj.dimension_id)
            cat_id = payload.get("category_id", obj.category_id)
            dimension, category = await self._validate_dimension_and_category(dim_id, cat_id)
            # 如果修改了 dimension_id 或 category_id，自动更新 category 和 subcategory
            payload["category"] = dimension.name
            payload["subcategory"] = category.name
        
        # 唯一性：若修改了 dimension_id/category_id/prompt 也需校验
        changed_keys = {k for k in payload.keys() if k in {"dimension_id", "category_id", "prompt"}}
        if changed_keys:
            check = {
                "dimension_id": payload.get("dimension_id", obj.dimension_id),
                "category_id": payload.get("category_id", obj.category_id),
                "prompt": payload.get("prompt", obj.prompt),
            }
            await self._ensure_unique(check)
        new_obj = await self.crud.update_crud(id=id, data=TestCaseUpdateSchema(**payload))
        await self._create_version_snapshot(new_obj)
        return TestCaseOutSchema.model_validate(new_obj).model_dump()

    async def delete(self, ids: List[int]) -> None:
        return await self.crud.delete_crud(ids=ids)

    async def list(self, search: Optional[Dict[str, Any]] = None, order_by: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
        rows = await self.crud.get_list_crud(search=search, order_by=order_by)
        return [TestCaseOutSchema.model_validate(r).model_dump() for r in rows]

    async def page(self, offset: int, limit: int, order_by: List[Dict[str, str]], search: Dict[str, Any]):
        return await self.crud.page_list_crud(offset=offset, limit=limit, order_by=order_by, search=search)

    async def import_items(self, items: List[TestCaseCreateSchema]) -> Dict[str, int]:
        created = 0
        skipped = 0
        for item in items:
            try:
                await self.create(item)
                created += 1
            except CustomException:
                skipped += 1
        return {"created": created, "skipped": skipped}

    async def export_items(self, search: Optional[Dict[str, Any]] = None):
        rows = await self.list(search=search)
        data = []
        for r in rows:
            data.append({
                "id": r["id"],
                "category": r["category"],
                "subcategory": r.get("subcategory"),
                "prompt": r["prompt"],
                "expected_behavior": r.get("expected_behavior"),
                "risk_level": r["risk_level"],
                "tags": r.get("tags", {}).get("items") if r.get("tags") else None,
                "status": r["status"],
                "version": r["version"],
                "description": r.get("description"),
                "created_at": r.get("created_at"),
                "updated_at": r.get("updated_at"),
            })
        return data

    async def export_testcase_list_service(self, testcase_list: List[Dict[str, Any]]) -> bytes:
        """
        导出测试用例列表为Excel文件
        
        参数:
        - testcase_list (List[Dict[str, Any]]): 测试用例列表
        
        返回:
        - bytes: Excel文件字节流
        """
        if not testcase_list:
            raise CustomException(msg="没有数据可导出")
            
        # 定义字段映射
        mapping_dict = {
            'id': '用例编号',
            'category': '类别',
            'subcategory': '子类别',
            'prompt': '提示词',
            'expected_behavior': '期望行为',
            'risk_level': '风险等级',
            'tags': '标签',
            'status': '状态',
            'version': '版本',
            'description': '描述',
            'created_at': '创建时间',
            'updated_at': '更新时间',
        }

        # 复制数据并转换
        data = testcase_list.copy()
        for item in data:
            # 状态转换
            item['status'] = '启用' if item.get('status') else '停用'
            # 风险等级转换
            risk_level = item.get('risk_level', '').lower()
            if risk_level == 'high':
                item['risk_level'] = '高'
            elif risk_level == 'medium':
                item['risk_level'] = '中'
            elif risk_level == 'low':
                item['risk_level'] = '低'
            else:
                item['risk_level'] = risk_level
            # 标签转换（如果是列表，转换为字符串）
            tags = item.get('tags')
            if isinstance(tags, list):
                item['tags'] = ','.join(str(tag) for tag in tags) if tags else ''
            elif tags is None:
                item['tags'] = ''

        return ExcelUtil.export_list2excel(list_data=data, mapping_dict=mapping_dict)

    async def _create_version_snapshot(self, tc: TestCaseModel) -> None:
        snapshot = {
            "dimension_id": tc.dimension_id,
            "category_id": tc.category_id,
            "category": tc.category,
            "subcategory": tc.subcategory,
            "prompt": tc.prompt,
            "expected_behavior": tc.expected_behavior,
            "risk_level": tc.risk_level,
            "tags": tc.tags,
            "status": tc.status,
            "description": tc.description,
        }
        version = TestCaseVersionModel(test_case_id=tc.id, snapshot=snapshot, version=tc.version)
        self.db.add(version)
        await self.db.flush()


