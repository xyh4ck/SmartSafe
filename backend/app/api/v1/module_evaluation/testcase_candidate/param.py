# -*- coding: utf-8 -*-

from typing import Optional
from fastapi import Query


class TestCaseCandidateQueryParam:
    """候选题池查询参数"""

    dimension_id: Optional[int]
    category_id: Optional[int]
    refusal_expectation: Optional[str]
    status: Optional[str]
    gen_batch_id: Optional[str]

    def __init__(
        self,
        dimension_id: Optional[int] = Query(None, description="维度ID"),
        category_id: Optional[int] = Query(None, description="分类ID"),
        refusal_expectation: Optional[str] = Query(None, description="拒答期望：should_refuse/should_not_refuse"),
        status: Optional[str] = Query(None, description="状态：pending_review/approved/rejected"),
        gen_batch_id: Optional[str] = Query(None, description="生成批次ID"),
    ) -> None:
        self.dimension_id = dimension_id
        self.category_id = category_id
        self.refusal_expectation = refusal_expectation
        self.status = status
        self.gen_batch_id = gen_batch_id
