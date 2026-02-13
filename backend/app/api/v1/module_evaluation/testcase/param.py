# -*- coding: utf-8 -*-

from typing import Optional, Tuple, Any, List
from fastapi import Query

from app.core.validator import DateTimeStr


class TestCaseQueryParam:
    """测试用例管理查询参数"""

    dimension_id: Optional[Tuple[str, List[int]]]
    category_id: Optional[Tuple[str, List[int]]]
    category: Optional[Tuple[str, Optional[str]]]
    risk_level: Optional[str]
    status: Optional[bool]
    creator_id: Optional[int]
    created_at: Optional[Tuple[str, Tuple[Any, Any]]]
    refusal_expectation: Optional[str]

    def __init__(
        self,
        dimension_id: Optional[int] = Query(None, description="维度ID（单个）"),
        dimension_ids: Optional[str] = Query(None, description="维度ID列表（逗号分隔）"),
        category_id: Optional[int] = Query(None, description="分类ID（单个）"),
        category_ids: Optional[str] = Query(None, description="分类ID列表（逗号分隔）"),
        category: Optional[str] = Query(None, description="类别"),
        risk_level: Optional[str] = Query(None, description="风险等级"),
        status: Optional[bool] = Query(None, description="是否启用"),
        start_time: Optional[DateTimeStr] = Query(None, description="开始时间", example="2025-01-01 00:00:00"),
        end_time: Optional[DateTimeStr] = Query(None, description="结束时间", example="2025-12-31 23:59:59"),
        creator: Optional[int] = Query(None, description="创建人"),
        refusal_expectation: Optional[str] = Query(None, description="拒答期望：should_refuse/should_not_refuse"),
    ) -> None:
        # 维度ID查询：支持单个或多个
        if dimension_ids:
            # 多个维度ID（逗号分隔字符串）
            id_list = [int(x.strip()) for x in dimension_ids.split(",") if x.strip().isdigit()]
            self.dimension_id = ("in", id_list) if id_list else None
        elif dimension_id is not None:
            # 单个维度ID
            self.dimension_id = dimension_id
        else:
            self.dimension_id = None
        
        # 分类ID查询：支持单个或多个
        if category_ids:
            # 多个分类ID（逗号分隔字符串）
            id_list = [int(x.strip()) for x in category_ids.split(",") if x.strip().isdigit()]
            self.category_id = ("in", id_list) if id_list else None
        elif category_id is not None:
            # 单个分类ID
            self.category_id = category_id
        else:
            self.category_id = None
        
        # 模糊查询
        self.category = ("like", category) if category else None

        # 精确查询
        self.risk_level = risk_level
        self.status = status
        self.creator_id = creator
        self.refusal_expectation = refusal_expectation

        # 时间范围查询（创建时间）
        if start_time and end_time:
            self.created_at = ("between", (start_time, end_time))
        else:
            self.created_at = None


