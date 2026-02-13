# -*- coding: utf-8 -*-

from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict

from app.core.base_schema import BaseSchema

if TYPE_CHECKING:
    from app.api.v1.module_evaluation.category.schema import CategoryOutSchema


class DimensionCreateSchema(BaseModel):
    name: str = Field(..., max_length=64, description='维度名称')
    code: Optional[str] = Field(default=None, max_length=64, description='维度代码')
    sort: int = Field(default=0, description='排序')
    status: bool = Field(default=True, description='是否启用')
    description: Optional[str] = Field(default=None, max_length=255, description='备注')


class DimensionUpdateSchema(DimensionCreateSchema):
    id: Optional[int] = Field(default=None, description='主键ID')


class DimensionOutSchema(DimensionCreateSchema, BaseSchema):
    model_config = ConfigDict(from_attributes=True)


class DimensionWithCategoriesSchema(DimensionOutSchema):
    """维度带分类列表"""
    # 使用字符串形式的前向引用，避免循环导入
    categories: List["CategoryOutSchema"] = Field(default_factory=list, description='分类列表')
    
    model_config = ConfigDict(from_attributes=True)


# 在文件末尾导入，确保 Pydantic 可以解析前向引用
from app.api.v1.module_evaluation.category.schema import CategoryOutSchema

# 更新前向引用
DimensionWithCategoriesSchema.model_rebuild()

