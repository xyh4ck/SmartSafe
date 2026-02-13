# -*- coding: utf-8 -*-

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.core.base_model import ModelMixin


class TenantModel(ModelMixin):
    """
    租户表
    """
    __tablename__ = 'system_tenant'
    __table_args__ = ({'comment': '租户表'})

    name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default='', comment='租户名称')
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default='', comment='租户编码')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """验证名称不为空"""
        if not name or not name.strip():
            raise ValueError('名称不能为空')
        return name
    
    @validates('code')
    def validate_code(self, key: str, code: str) -> str:
        """验证编码格式校验"""
        if not code or not code.strip():
            raise ValueError('编码不能为空')
        if not code.isalnum():
            raise ValueError('编码只能包含字母和数字')
        return code

