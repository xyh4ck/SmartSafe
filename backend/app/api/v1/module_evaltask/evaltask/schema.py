# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class EvalCaseCreateSchema(BaseModel):
    prompt: str = Field(..., description="测试用例提示词")
    llm_provider: Optional[str] = Field(default=None, description="大模型提供方")
    llm_params: Optional[dict[str, Any]] = Field(default=None, description="模型参数")


class EvalTaskCreateSchema(BaseModel):
    name: str = Field(..., description="任务名称")
    cases: List[EvalCaseCreateSchema] = Field(..., description="测试用例列表")


class EvalTaskIdSchema(BaseModel):
    task_id: int = Field(..., description="任务ID")


class EvalTaskQuerySchema(BaseModel):
    status: Optional[str] = Field(default=None, description="任务状态过滤")
    name: Optional[str] = Field(default=None, description="按名称模糊查询")


class EvalTaskProgressSchema(BaseModel):
    task_id: int
    status: str
    finished: int
    total: int
    percent: float


class EvalTaskCaseSchema(BaseModel):
    id: int
    prompt: str
    status: str
    output_text: Optional[str]
    llm_provider: Optional[str]
    risk_scores: Optional[dict[str, float]]
    risk_level: Optional[str]
    risk_reason: Optional[str]
    completion_tokens: Optional[int]
    prompt_tokens: Optional[int]
    total_tokens: Optional[int]


class EvalTaskDetailSchema(BaseModel):
    id: int
    name: str
    status: str
    total_cases: int
    finished_cases: int
    risk_summary: Optional[dict[str, Any]]


class EvalTaskResultSchema(BaseModel):
    task_id: int
    summary: dict[str, Any]
    metrics: dict[str, Any]
    top_risks: list[dict[str, Any]]
