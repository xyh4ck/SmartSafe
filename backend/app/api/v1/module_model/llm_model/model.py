from typing import Optional
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import CreatorMixin


class ModelRegistryModel(CreatorMixin):
    __tablename__ = "app_model_registry"
    __table_args__ = {"comment": "模型接入管理"}
    __loader_options__ = ["creator"]

    name: Mapped[str] = mapped_column(String(100), unique=True, comment="模型名称")
    provider: Mapped[str] = mapped_column(String(50), comment="模型提供商")
    type: Mapped[int] = mapped_column(String(50), default=0, comment="模型类型")
    api_base: Mapped[Optional[str]] = mapped_column(String(255), default=None, comment="API基础地址")
    api_key_enc: Mapped[Optional[str]] = mapped_column(String(1024), default=None, comment="加密的API密钥")
    available: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可用")
    version: Mapped[Optional[str]] = mapped_column(String(50), default=None, comment="模型版本")
    quota_limit: Mapped[int] = mapped_column(Integer, default=0, comment="配额限制")
    quota_used: Mapped[int] = mapped_column(Integer, default=0, comment="已使用配额")
    description: Mapped[Optional[str]] = mapped_column(String(255), default=None, comment="模型描述")
