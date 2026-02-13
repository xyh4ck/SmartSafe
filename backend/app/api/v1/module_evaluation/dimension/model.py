# -*- coding: utf-8 -*-

from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import CreatorMixin


class DimensionModel(CreatorMixin):
    """
    测试用例维度表
    """

    __tablename__ = "evaluation_dimension"
    __table_args__ = ({'comment': '测试用例维度表'})
    __loader_options__ = ["creator"]

    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True, comment='维度名称')
    code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, unique=True, index=True, comment='维度代码')
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='排序')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment='是否启用')

    categories: Mapped[List["CategoryModel"]] = relationship(
        back_populates="dimension",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

