# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional


class CacheMonitorSchema(BaseModel):
    """缓存监控信息模型"""
    model_config = ConfigDict(from_attributes=True)

    command_stats: List[Dict] = Field(default_factory=list, description='Redis命令统计信息')
    db_size: int = Field(default=0, description='Redis数据库中的Key总数')
    info: Dict[str, Any] = Field(default_factory=dict, description='Redis服务器信息')


class CacheInfoSchema(BaseModel):
    """缓存对象信息模型"""
    model_config = ConfigDict(from_attributes=True)

    cache_key: str = Field(..., description='缓存键名')
    cache_name: str = Field(..., description='缓存名称')
    cache_value: Any = Field(default=None, description='缓存值')
    remark: Optional[str] = Field(default=None, description='备注说明')
