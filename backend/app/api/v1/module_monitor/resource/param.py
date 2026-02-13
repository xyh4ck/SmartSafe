# -*- coding: utf-8 -*-

from typing import Optional
from fastapi import Query

class ResourceSearchQueryParam:
    """资源搜索查询参数"""

    def __init__(
        self,
        name: Optional[str] = Query(None, description="搜索关键词"),
        path: Optional[str] = Query(None, description="目录路径"),
    ) -> None:
        
        # 模糊查询字段
        self.name = ("like", name) if name else None
        
        # 精确查询字段
        self.path = path