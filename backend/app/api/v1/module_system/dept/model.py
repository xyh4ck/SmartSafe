# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.base_model import ModelMixin

if TYPE_CHECKING:
    from app.api.v1.module_system.role.model import RoleModel
    from app.api.v1.module_system.user.model import UserModel

class DeptModel(ModelMixin):
    """
    部门表
    """
    __tablename__ = "system_dept"
    __table_args__ = ({'comment': '部门表'})
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    # 基础字段
    name: Mapped[str] = mapped_column(String(40),nullable=False,unique=True,comment="部门名称")
    order: Mapped[int] = mapped_column(Integer,nullable=False,default=999,comment="显示排序")
    code: Mapped[Optional[str]] = mapped_column(String(20),nullable=True,unique=True,comment="部门编码")
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("system_dept.id", ondelete="SET NULL", onupdate="CASCADE"), default=None, index=True, comment="父级部门ID")    
    parent: Mapped[Optional['DeptModel']] = relationship(back_populates='children', remote_side=[id],uselist=False)
    children: Mapped[Optional[List['DeptModel']]] = relationship(back_populates='parent')

    # 角色关联关系
    roles: Mapped[List["RoleModel"]] = relationship(secondary="system_role_depts", back_populates="depts", lazy="selectin")
    
    # 用户关联关系
    users: Mapped[List["UserModel"]] = relationship(back_populates="dept", lazy="selectin")