# -*- coding: utf-8 -*-

from typing import Optional
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import CreatorMixin


class CategoryModel(CreatorMixin):
    """
    测试用例分类表
    """

    __tablename__ = "evaluation_category"
    __table_args__ = ({'comment': '测试用例分类表'})
    __loader_options__ = ["creator"]

    dimension_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('evaluation_dimension.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment='维度ID'
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment='分类名称')
    code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True, comment='分类代码')
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='排序')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment='是否启用')

    dimension: Mapped["DimensionModel"] = relationship(
        back_populates="categories",
        lazy="selectin"
    )

