# -*- coding: utf-8 -*-

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.core.base_schema import BaseSchema


class TestCaseCreateSchema(BaseModel):
    dimension_id: int = Field(..., description='维度ID')
    category_id: int = Field(..., description='分类ID')
    category: Optional[str] = Field(default=None, max_length=64, description='风险类别（兼容字段，自动填充）')
    subcategory: Optional[str] = Field(default=None, max_length=64, description='子类别（兼容字段，自动填充）')
    prompt: str = Field(..., description='测试提示')
    expected_behavior: Optional[str] = Field(default=None, description='期望行为')
    risk_level: str = Field(..., max_length=32, description='风险等级')
    tags: Optional[List[str]] = Field(default=None, description='标签数组')
    status: bool = Field(default=True, description='是否启用')
    description: Optional[str] = Field(default=None, max_length=255, description='备注')
    # 拒答题库新增字段
    refusal_expectation: Optional[str] = Field(default=None, max_length=32, description='拒答期望：should_refuse/should_not_refuse')
    refusal_reason: Optional[str] = Field(default=None, description='拒答理由要求/合规话术要求')
    source: Optional[str] = Field(default=None, max_length=32, description='来源：manual/import/generated')
    updated_cycle: Optional[str] = Field(default=None, max_length=16, description='更新周期标记：YYYY-MM')

    @field_validator("tags", mode="before")
    @classmethod
    def _norm_tags(cls, value):
        if value is None:
            return None
        # 兼容前端可能传入 {"items": [...]} 的形式
        if isinstance(value, dict) and "items" in value and isinstance(value.get("items"), list):
            value = value["items"]
        if not isinstance(value, list):
            raise TypeError("tags must be a list of strings")
        return [str(v).strip() for v in value if str(v).strip() != ""]


class TestCaseUpdateSchema(TestCaseCreateSchema):
    id: Optional[int] = Field(default=None, description='主键ID')
    version: Optional[int] = Field(default=None, description='当前版本（编辑时自动递增）')


class TestCaseOutSchema(TestCaseCreateSchema, BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    version: int = Field(..., description='当前版本')


class ImportTestCaseSchema(BaseModel):
    items: List[TestCaseCreateSchema]


class ExportQuerySchema(BaseModel):
    # 可加筛选导出
    category: Optional[str] = Field(default=None)
    risk_level: Optional[str] = Field(default=None)


