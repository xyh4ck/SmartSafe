# -*- coding: utf-8 -*-

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import CreatorMixin

if TYPE_CHECKING:
    from app.api.v1.module_evaluation.dimension.model import DimensionModel
    from app.api.v1.module_evaluation.category.model import CategoryModel


class TestCaseModel(CreatorMixin):
    """
    测试用例表
    """

    __tablename__ = "evaluation_test_case"
    __table_args__ = {"comment": "测试用例表"}
    __loader_options__ = ["creator"]

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
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="风险类别（兼容字段）"
    )
    subcategory: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="子类别（兼容字段）"
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False, comment="测试提示")
    expected_behavior: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="期望行为"
    )
    risk_level: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True, comment="风险等级"
    )
    # 使用 JSON 存储标签，兼容 PostgreSQL / MySQL8 / SQLite
    tags: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="标签（数组）"
    )
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="当前版本"
    )
    status: Mapped[bool] = mapped_column(
        Boolean(), default=True, nullable=False, comment="是否启用"
    )
    # 拒答题库新增字段
    refusal_expectation: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, index=True, comment="拒答期望：should_refuse/should_not_refuse"
    )
    refusal_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="拒答理由要求/合规话术要求"
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="来源：manual/import/generated"
    )
    updated_cycle: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="更新周期标记：YYYY-MM"
    )

    versions: Mapped[list["TestCaseVersionModel"]] = relationship(
        back_populates="test_case", cascade="all, delete-orphan", lazy="selectin"
    )

    dimension: Mapped["DimensionModel"] = relationship(
        foreign_keys=[dimension_id], lazy="selectin"
    )

    category_rel: Mapped["CategoryModel"] = relationship(
        foreign_keys=[category_id], lazy="selectin"
    )


class TestCaseVersionModel(CreatorMixin):
    """
    测试用例版本历史表
    """

    __tablename__ = "evaluation_test_case_version"
    __table_args__ = {"comment": "测试用例版本历史表"}

    test_case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evaluation_test_case.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="测试用例ID",
    )
    snapshot: Mapped[dict] = mapped_column(
        JSON, nullable=False, comment="用例快照(JSON)"
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, comment="版本号")

    test_case: Mapped["TestCaseModel"] = relationship(
        back_populates="versions", lazy="selectin"
    )
