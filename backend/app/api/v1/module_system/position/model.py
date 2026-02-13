# -*- coding: utf-8 -*-
"""
岗位模型模块
定义岗位相关数据模型
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.base_model import CreatorMixin

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel


class PositionModel(CreatorMixin):
    """
    岗位模型
    """
    __tablename__ = "system_position"
    __table_args__ = ({'comment': '岗位表'})
    __loader_options__ = ["creator"]

    name: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, comment="岗位名称")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="显示排序")
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")

    # 用户关联关系
    users: Mapped[List["UserModel"]] = relationship(secondary="system_user_positions", back_populates="positions", lazy="selectin")


