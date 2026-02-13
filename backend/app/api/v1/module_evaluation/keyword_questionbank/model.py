# -*- coding: utf-8 -*-

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import CreatorMixin

if TYPE_CHECKING:
    from app.api.v1.module_evaluation.category.model import CategoryModel


class KeywordModel(CreatorMixin):
    """
    关键词表 - 存储关键词及其与分类的关联
    使用现有的 CategoryModel 作为分类
    """

    __tablename__ = "evaluation_keyword"
    __table_args__ = (
        Index("idx_keyword_category", "category_id"),
        Index("idx_keyword_word", "word"),
        {"comment": "关键词表"}
    )
    __loader_options__ = ["creator"]

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evaluation_category.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="分类ID（关联evaluation_category表）"
    )
    word: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="关键词"
    )
    match_type: Mapped[str] = mapped_column(
        String(32), default="exact", nullable=False, 
        comment="匹配类型: exact(精确), fuzzy(模糊), regex(正则)"
    )
    risk_level: Mapped[str] = mapped_column(
        String(32), default="medium", nullable=False, index=True, 
        comment="风险等级(high/medium/low)"
    )
    weight: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="权重（用于评分计算）"
    )
    synonyms: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="同义词列表（JSON数组）"
    )
    tags: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="标签（JSON数组）"
    )
    status: Mapped[bool] = mapped_column(
        Boolean(), default=True, nullable=False, comment="是否启用"
    )
    hit_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="命中次数（统计用）"
    )

    # 关联分类
    category: Mapped["CategoryModel"] = relationship(
        foreign_keys=[category_id],
        lazy="selectin"
    )
