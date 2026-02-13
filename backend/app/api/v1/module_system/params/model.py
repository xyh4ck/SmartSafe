# -*- coding: utf-8 -*-

from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import CreatorMixin


class ParamsModel(CreatorMixin):
    """
    系统配置表
    """
    __tablename__ = "system_param"
    __table_args__ = ({'comment': '系统参数表'})
    __loader_options__ = ["creator"]

    # 基础字段
    config_name: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, comment='参数名称')
    config_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, comment='参数键名')
    config_value: Mapped[Optional[str]] = mapped_column(String(500), comment='参数键值')
    config_type: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True, comment="系统内置(True:是 False:否)")
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")


