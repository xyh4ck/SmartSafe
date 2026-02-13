# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, JSON, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import CreatorMixin

if TYPE_CHECKING:
    from app.api.v1.module_evaluation.dimension.model import DimensionModel
    from app.api.v1.module_evaluation.category.model import CategoryModel
    from app.api.v1.module_system.user.model import UserModel


class TestCaseCandidateModel(CreatorMixin):
    """
    测试用例候选题池表
    """

    __tablename__ = "evaluation_test_case_candidate"
    __table_args__ = {"comment": "测试用例候选题池"}
    __loader_options__ = ["creator", "reviewer"]

    dimension_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evaluation_dimension.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="维度ID",
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evaluation_category.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="分类ID",
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False, comment="测试提示")
    expected_behavior: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="期望行为"
    )
    risk_level: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="风险等级"
    )
    tags: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="标签（数组）"
    )
    refusal_expectation: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, index=True, comment="拒答期望：should_refuse/should_not_refuse"
    )
    refusal_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="拒答理由要求"
    )
    gen_batch_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True, comment="生成批次ID"
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending_review", comment="状态：pending_review/approved/rejected"
    )
    reviewer_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("system_users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="审核人ID",
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="审核时间"
    )
    review_note: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="审核备注"
    )

    dimension: Mapped["DimensionModel"] = relationship(
        foreign_keys=[dimension_id], lazy="selectin"
    )

    category_rel: Mapped["CategoryModel"] = relationship(
        foreign_keys=[category_id], lazy="selectin"
    )

    reviewer: Mapped[Optional["UserModel"]] = relationship(
        foreign_keys=[reviewer_id], lazy="selectin"
    )
