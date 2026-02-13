# -*- coding: utf-8 -*-

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.core.base_schema import BaseSchema


# ==================== 关键词 Schema ====================

class KeywordCreateSchema(BaseModel):
    """创建关键词"""
    category_id: int = Field(..., description="分类ID（关联evaluation_category表）")
    word: str = Field(..., max_length=255, description="关键词")
    match_type: str = Field(default="exact", max_length=32, description="匹配类型")
    risk_level: str = Field(default="medium", max_length=32, description="风险等级")
    weight: int = Field(default=1, ge=1, le=100, description="权重")
    synonyms: Optional[List[str]] = Field(default=None, description="同义词列表")
    tags: Optional[List[str]] = Field(default=None, description="标签数组")
    status: bool = Field(default=True, description="是否启用")
    description: Optional[str] = Field(default=None, max_length=255, description="备注")

    @field_validator("match_type", mode="before")
    @classmethod
    def _norm_match_type(cls, value):
        v = str(value).lower().strip()
        if v not in ("exact", "fuzzy", "regex"):
            return "exact"
        return v

    @field_validator("risk_level", mode="before")
    @classmethod
    def _norm_risk_level(cls, value):
        v = str(value).lower().strip()
        if v in ("high", "高"):
            return "high"
        if v in ("medium", "中"):
            return "medium"
        if v in ("low", "低"):
            return "low"
        return "medium"

    @field_validator("synonyms", mode="before")
    @classmethod
    def _norm_synonyms(cls, value):
        if value is None:
            return None
        if isinstance(value, dict) and "items" in value:
            value = value["items"]
        if not isinstance(value, list):
            return None
        return [str(v).strip() for v in value if str(v).strip()]

    @field_validator("tags", mode="before")
    @classmethod
    def _norm_tags(cls, value):
        if value is None:
            return None
        if isinstance(value, dict) and "items" in value:
            value = value["items"]
        if not isinstance(value, list):
            return None
        return [str(v).strip() for v in value if str(v).strip()]


class KeywordUpdateSchema(KeywordCreateSchema):
    """更新关键词"""
    id: Optional[int] = Field(default=None, description="主键ID")
    hit_count: Optional[int] = Field(default=None, description="命中次数")


class KeywordOutSchema(KeywordCreateSchema, BaseSchema):
    """关键词输出"""
    model_config = ConfigDict(from_attributes=True)
    hit_count: int = Field(default=0, description="命中次数")
    category_name: Optional[str] = Field(default=None, description="分类名称")


# ==================== 批量操作 Schema ====================

class ImportKeywordSchema(BaseModel):
    """批量导入关键词"""
    items: List[KeywordCreateSchema]


# ==================== 匹配相关 Schema ====================

class KeywordMatchRequest(BaseModel):
    """关键词匹配请求"""
    text: str = Field(..., description="待匹配文本")
    category_ids: Optional[List[int]] = Field(default=None, description="限定分类ID列表")
    match_types: Optional[List[str]] = Field(default=None, description="限定匹配类型")
    min_risk_level: Optional[str] = Field(default=None, description="最低风险等级")


class KeywordMatchResult(BaseModel):
    """关键词匹配结果"""
    keyword_id: int = Field(..., description="关键词ID")
    word: str = Field(..., description="匹配到的关键词")
    match_type: str = Field(..., description="匹配类型")
    risk_level: str = Field(..., description="风险等级")
    category_id: int = Field(..., description="分类ID")
    category_name: str = Field(..., description="分类名称")
    weight: int = Field(..., description="权重")
    position: Optional[int] = Field(default=None, description="匹配位置")
    matched_text: Optional[str] = Field(default=None, description="实际匹配到的文本")


class KeywordMatchResponse(BaseModel):
    """关键词匹配响应"""
    total_matches: int = Field(..., description="总匹配数")
    risk_score: float = Field(..., description="风险评分")
    highest_risk_level: str = Field(..., description="最高风险等级")
    matches: List[KeywordMatchResult] = Field(..., description="匹配结果列表")
