# -*- coding: utf-8 -*-
"""
通知公告模型模块
定义通知公告相关数据模型
"""

from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import CreatorMixin


class NoticeModel(CreatorMixin):
    """
    通知公告模型

    类型：
    - 1: 通知
    - 2: 公告
    """
    __tablename__ = "system_notice"
    __table_args__ = ({'comment': '通知公告表'})
    __loader_options__ = ["creator"]

    notice_title: Mapped[str] = mapped_column(String(50), nullable=False, comment='公告标题')
    notice_type: Mapped[str] = mapped_column(String(50), nullable=False, comment='公告类型（1通知 2公告）')
    notice_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='公告内容')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
