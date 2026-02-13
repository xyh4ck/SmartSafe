# -*- coding: utf-8 -*-

from typing import Optional, List
from sqlalchemy import Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.base_model import CreatorMixin


class DictTypeModel(CreatorMixin):
    """
    字典类型表
    """

    __tablename__ = "system_dict_type"
    __table_args__ = ({'comment': '字典类型表'})
    __loader_options__ = ["creator"]

    dict_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment='字典名称')
    dict_type: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment='字典类型')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    dict_datas: Mapped[List["DictDataModel"]] = relationship(back_populates="dict_type_rel", lazy="selectin")


class DictDataModel(CreatorMixin):
    """
    字典数据表
    """

    __tablename__ = 'system_dict_data'
    __table_args__ = ({'comment': '字典数据表'})
    __loader_options__ = ["creator"]

    dict_sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='字典排序')
    dict_label: Mapped[str] = mapped_column(String(100), nullable=False, comment='字典标签')
    dict_value: Mapped[str] = mapped_column(String(100), nullable=False, comment='字典键值')
    dict_type: Mapped[str] = mapped_column(String(100), nullable=False, comment='字典类型')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    css_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='样式属性（其他样式扩展）')
    list_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='表格回显样式')
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment='是否默认（True是 False否）')
    dict_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey('system_dict_type.id'), nullable=True, comment='字典类型ID')
    
    # 字典类型关联关系
    dict_type_rel: Mapped[Optional["DictTypeModel"]] = relationship(back_populates="dict_datas", lazy="selectin")

