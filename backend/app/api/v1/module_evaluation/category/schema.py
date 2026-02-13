# -*- coding: utf-8 -*-

from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict

from app.core.base_schema import BaseSchema

if TYPE_CHECKING:
    from app.api.v1.module_evaluation.dimension.schema import DimensionOutSchema


class CategoryCreateSchema(BaseModel):
    dimension_id: int = Field(..., description="维度ID")
    name: str = Field(..., max_length=64, description="分类名称")
    code: Optional[str] = Field(default=None, max_length=64, description="分类代码")
    sort: int = Field(default=0, description="排序")
    status: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(default=None, max_length=255, description="备注")


class CategoryUpdateSchema(CategoryCreateSchema):
    id: Optional[int] = Field(default=None, description="主键ID")


class CategoryOutSchema(CategoryCreateSchema, BaseSchema):
    model_config = ConfigDict(from_attributes=True)


class CategoryWithDimensionSchema(CategoryOutSchema):
    """分类带维度信息"""

    dimension: Optional["DimensionOutSchema"] = Field(default=None, description="维度信息")

    model_config = ConfigDict(from_attributes=True)


from app.api.v1.module_evaluation.dimension.schema import DimensionOutSchema

CategoryWithDimensionSchema.model_rebuild()
