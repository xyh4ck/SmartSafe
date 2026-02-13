# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.core.base_schema import BaseSchema


class TestCaseCandidateCreateSchema(BaseModel):
    dimension_id: int = Field(..., description='维度ID')
    category_id: int = Field(..., description='分类ID')
    prompt: str = Field(..., description='测试提示')
    expected_behavior: Optional[str] = Field(default=None, description='期望行为')
    risk_level: str = Field(..., max_length=32, description='风险等级')
    tags: Optional[List[str]] = Field(default=None, description='标签数组')
    refusal_expectation: Optional[str] = Field(default=None, max_length=32, description='拒答期望：should_refuse/should_not_refuse')
    refusal_reason: Optional[str] = Field(default=None, description='拒答理由要求')
    gen_batch_id: Optional[str] = Field(default=None, max_length=64, description='生成批次ID')
    description: Optional[str] = Field(default=None, max_length=255, description='备注')

    @field_validator("tags", mode="before")
    @classmethod
    def _norm_tags(cls, value):
        if value is None:
            return None
        if isinstance(value, dict) and "items" in value and isinstance(value.get("items"), list):
            value = value["items"]
        if not isinstance(value, list):
            raise TypeError("tags must be a list of strings")
        return [str(v).strip() for v in value if str(v).strip() != ""]


class TestCaseCandidateUpdateSchema(BaseModel):
    id: Optional[int] = Field(default=None, description='主键ID')
    status: Optional[str] = Field(default=None, max_length=32, description='状态：pending_review/approved/rejected')
    review_note: Optional[str] = Field(default=None, description='审核备注')


class TestCaseCandidateOutSchema(TestCaseCandidateCreateSchema, BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    status: str = Field(..., description='状态')
    reviewer_id: Optional[int] = Field(default=None, description='审核人ID')
    reviewed_at: Optional[datetime] = Field(default=None, description='审核时间')
    review_note: Optional[str] = Field(default=None, description='审核备注')
    dimension_name: Optional[str] = Field(default=None, description='维度名称')
    category_name: Optional[str] = Field(default=None, description='分类名称')


class BatchReviewSchema(BaseModel):
    ids: List[int] = Field(..., description='候选题ID列表')
    action: str = Field(..., description='操作：approve/reject')
    review_note: Optional[str] = Field(default=None, description='审核备注')


class BatchPublishSchema(BaseModel):
    ids: List[int] = Field(..., description='候选题ID列表（仅approved状态可发布）')


class GenerateCandidateSchema(BaseModel):
    refusal_expectation: str = Field(..., description='拒答期望：should_refuse/should_not_refuse')
    category_ids: Optional[List[int]] = Field(default=None, description='指定分类ID列表（不传则自动根据缺口生成）')
    count_per_category: int = Field(default=5, ge=1, le=50, description='每个分类生成数量')
