# -*- coding: utf-8 -*-
"""
用户模型模块
定义用户相关数据模型和关联表
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.api.v1.module_system.dept.model import DeptModel
from app.api.v1.module_system.position.model import PositionModel
from app.api.v1.module_system.role.model import RoleModel
from app.core.base_model import MappedBase


class UserRolesModel(MappedBase):
    """
    用户角色关联表
    
    定义用户与角色的多对多关系
    """
    __tablename__ = "system_user_roles"
    __table_args__ = ({'comment': '用户角色关联表'})

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_users.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="用户ID"
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="角色ID"
    )


class UserPositionsModel(MappedBase):
    """
    用户岗位关联表
    
    定义用户与岗位的多对多关系
    """
    __tablename__ = "system_user_positions"
    __table_args__ = ({'comment': '用户岗位关联表'})

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_users.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="用户ID"
    )
    position_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_position.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="岗位ID"
    )


class UserModel(MappedBase):
    """
    用户模型
    """
    __tablename__ = "system_users"
    __table_args__ = ({'comment': '用户表'})
    __loader_options__ = ["dept", "roles", "positions", "creator"]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    
    username: Mapped[str] = mapped_column(String(32),nullable=False,unique=True,comment="用户名/登录账号")
    password: Mapped[str] = mapped_column(String(255),nullable=False,comment="密码哈希")
    name: Mapped[str] = mapped_column(String(32),nullable=False,comment="昵称")
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    mobile: Mapped[Optional[str]] = mapped_column(String(20),nullable=True,unique=True,comment="手机号")
    email: Mapped[Optional[str]] = mapped_column(String(64),nullable=True,unique=True,comment="邮箱")
    gender: Mapped[Optional[str]] = mapped_column(String(1), default='0',nullable=True,comment="性别(0:男 1:女 2:未知)")
    avatar: Mapped[Optional[str]] = mapped_column(String(500),nullable=True,comment="头像URL地址")
    is_superuser: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False,comment="是否超管")
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True),nullable=True,comment="最后登录时间")
    
    dept_id: Mapped[Optional[int]] = mapped_column(Integer,ForeignKey('system_dept.id', ondelete="SET NULL", onupdate="CASCADE"),nullable=True, index=True, comment="部门ID")
    dept: Mapped[Optional["DeptModel"]] = relationship(back_populates="users",foreign_keys=[dept_id],lazy="selectin")
    roles: Mapped[List["RoleModel"]] = relationship(secondary="system_user_roles",back_populates="users",lazy="selectin")
    positions: Mapped[List["PositionModel"]] = relationship(secondary="system_user_positions",back_populates="users",lazy="selectin")

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None, comment="备注/描述")
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    creator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('system_users.id', ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True, comment="创建人ID")
    creator: Mapped[Optional["UserModel"]] = relationship(foreign_keys=[creator_id],lazy="selectin",remote_side=[id])