# -*- coding: utf-8 -*-
"""
菜单模型模块
定义系统菜单相关数据模型
"""

from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Boolean, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.base_model import ModelMixin

if TYPE_CHECKING:
    from app.api.v1.module_system.role.model import RoleModel


class MenuModel(ModelMixin):
    """
    菜单表 - 用于存储系统菜单信息 - SQLAlchemy 2.0 语法

    菜单类型说明:
    1: 目录
    2: 菜单 
    3: 按钮/权限
    4: 链接
    """
    __tablename__ = "system_menu"
    __table_args__ = ({'comment': '菜单表'})
    __loader_options__ = ["roles"]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment='菜单名称', unique=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False, default=2, comment='菜单类型(1:目录 2:菜单 3:按钮/权限 4:链接)')
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=999, comment='显示排序')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    permission: Mapped[Optional[str]] = mapped_column(String(100), comment='权限标识(如：module_system:user:list)')
    icon: Mapped[Optional[str]] = mapped_column(String(50), comment='菜单图标')
    route_name: Mapped[Optional[str]] = mapped_column(String(100), comment='路由名称')
    route_path: Mapped[Optional[str]] = mapped_column(String(200), comment='路由路径')
    component_path: Mapped[Optional[str]] = mapped_column(String(200), comment='组件路径')
    redirect: Mapped[Optional[str]] = mapped_column(String(200), comment='重定向地址')
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment='是否隐藏(True:隐藏 False:显示)')
    keep_alive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment='是否缓存(True:是 False:否)')
    always_show: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment='是否始终显示(True:是 False:否)')
    title: Mapped[Optional[str]] = mapped_column(String(50),  comment='菜单标题')
    params: Mapped[Optional[list[dict[str, str]]]] = mapped_column(JSON,  comment='路由参数(JSON对象)')
    affix: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment='是否固定标签页(True:是 False:否)')
    
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('system_menu.id', ondelete='SET NULL'), default=None, index=True, comment='父菜单ID')
    parent: Mapped[Optional['MenuModel']] = relationship(back_populates='children', remote_side=[id], uselist=False)
    children: Mapped[Optional[List['MenuModel']]] = relationship(back_populates='parent', order_by="MenuModel.order")
    
    # 角色关联关系
    roles: Mapped[List["RoleModel"]] = relationship(secondary="system_role_menus", back_populates="menus", lazy="selectin")
    
    # link: Mapped[Optional[str]] = mapped_column(String(255),  comment='外链地址')
    # iframe: Mapped[Optional[str]] = mapped_column(String(255),  comment='内嵌iframe地址')