# -*- coding: utf-8 -*-
"""
角色模型模块
定义角色相关数据模型和关联表
"""

from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.base_model import MappedBase, CreatorMixin

from app.api.v1.module_system.menu.model import MenuModel

if TYPE_CHECKING:
    from app.api.v1.module_system.dept.model import DeptModel
    from app.api.v1.module_system.user.model import UserModel


class RoleMenusModel(MappedBase):
    """
    角色菜单关联表
    
    定义角色与菜单的多对多关系，用于权限控制
    """
    __tablename__ = "system_role_menus"
    __table_args__ = ({'comment': '角色菜单关联表'})

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="角色ID"
    )
    menu_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_menu.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="菜单ID"
    )


class RoleDeptsModel(MappedBase):
    """
    角色部门关联表
    
    定义角色与部门的多对多关系，用于数据权限控制
    """
    __tablename__ = "system_role_depts"
    __table_args__ = ({'comment': '角色部门关联表'})

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="角色ID"
    )
    dept_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("system_dept.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="部门ID"
    )


class RoleModel(CreatorMixin):
    """
    角色模型
    
    data_scope 数据权限范围：
    - 1: 仅本人数据权限
    - 2: 本部门数据权限
    - 3: 本部门及以下数据权限
    - 4: 全部数据权限
    - 5: 自定义数据权限
    """
    __tablename__ = "system_role"
    __table_args__ = ({'comment': '角色表'})
    __loader_options__ = ["menus", "depts", "creator"]

    name: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, comment="角色名称")
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True, comment="角色编码")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=999, comment="显示排序")
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    data_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="数据权限范围")

    menus: Mapped[List["MenuModel"]] = relationship(secondary="system_role_menus", back_populates="roles", lazy="selectin", order_by="MenuModel.order")
    depts: Mapped[List["DeptModel"]] = relationship(secondary="system_role_depts", back_populates="roles", lazy="selectin")
    users: Mapped[List["UserModel"]] = relationship(secondary="system_user_roles", back_populates="roles", lazy="selectin")

