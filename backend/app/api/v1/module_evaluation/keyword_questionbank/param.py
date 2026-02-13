# -*- coding: utf-8 -*-

from typing import Optional, Tuple, Any, List
from fastapi import Query

from app.core.validator import DateTimeStr


class KeywordQueryParam:
    """关键词查询参数"""

    category_id: Optional[Tuple[str, List[int]]] | Optional[int]
    word: Optional[Tuple[str, Optional[str]]]
    match_type: Optional[str]
    risk_level: Optional[str]
    status: Optional[bool]
    creator_id: Optional[int]
    created_at: Optional[Tuple[str, Tuple[Any, Any]]]

    def __init__(
        self,
        category_id: Optional[int] = Query(None, description="分类ID（单个）"),
        category_ids: Optional[str] = Query(None, description="分类ID列表（逗号分隔）"),
        word: Optional[str] = Query(None, description="关键词（模糊查询）"),
        match_type: Optional[str] = Query(None, description="匹配类型"),
        risk_level: Optional[str] = Query(None, description="风险等级"),
        status: Optional[bool] = Query(None, description="是否启用"),
        start_time: Optional[DateTimeStr] = Query(None, description="开始时间"),
        end_time: Optional[DateTimeStr] = Query(None, description="结束时间"),
        creator: Optional[int] = Query(None, description="创建人"),
    ) -> None:
        # 分类ID查询：支持单个或多个
        if category_ids:
            id_list = [int(x.strip()) for x in category_ids.split(",") if x.strip().isdigit()]
            self.category_id = ("in", id_list) if id_list else None
        elif category_id is not None:
            self.category_id = category_id
        else:
            self.category_id = None

        # 模糊查询
        self.word = ("like", word) if word else None

        # 精确查询
        self.match_type = match_type
        self.risk_level = risk_level
        self.status = status
        self.creator_id = creator

        # 时间范围查询
        if start_time and end_time:
            self.created_at = ("between", (start_time, end_time))
        else:
            self.created_at = None
