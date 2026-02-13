# -*- coding: utf-8 -*-

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin


class EvalTaskModel(ModelMixin):
    __tablename__ = "eval_task"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="任务名称"
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="queued", index=True, comment="任务状态"
    )
    total_cases: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="总用例数"
    )
    finished_cases: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="完成用例数"
    )
    risk_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="风险汇总(JSON)"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None, comment="开始时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None, comment="完成时间"
    )


class EvalTaskCaseModel(ModelMixin):
    __tablename__ = "eval_task_case"

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("eval_task.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="任务ID",
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False, comment="测试用例提示词")
    llm_provider: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, default=None, comment="大模型提供方"
    )
    llm_params: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="模型参数(JSON)"
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="queued", index=True, comment="用例状态"
    )
    output_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="模型输出文本"
    )
    risk_scores: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="风险评分(JSON)"
    )
    risk_level: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, default=None, comment="风险等级"
    )
    risk_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="风险评估依据"
    )
    completion_tokens: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None, comment="完成token数"
    )
    prompt_tokens: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None, comment="提示token数"
    )
    total_tokens: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None, comment="总token数"
    )
    error: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="错误信息"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None, comment="开始时间"
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None, comment="完成时间"
    )


class EvalTaskResultModel(ModelMixin):
    __tablename__ = "eval_task_result"

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("eval_task.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
        comment="任务ID",
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="报告摘要(JSON)"
    )
    metrics: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="维度指标(JSON)"
    )
    top_risks: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="高风险样本(JSON)"
    )


class EvalTaskLogModel(ModelMixin):
    __tablename__ = "eval_task_log"

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("eval_task.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="任务ID",
    )
    case_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("eval_task_case.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
        comment="用例ID",
    )
    stage: Mapped[str] = mapped_column(String(64), nullable=False, comment="阶段")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="日志消息")
    level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="INFO", comment="日志等级"
    )
