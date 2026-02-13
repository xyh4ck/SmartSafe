# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, Body, Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import SuccessResponse
from app.common.request import PaginationService
from app.core.router_class import OperationLogRoute
from app.core.dependencies import db_getter, get_current_user
from app.core.base_params import PaginationQueryParam
from app.core.logger import logger
from .schema import EvalTaskCreateSchema, EvalTaskQuerySchema
from .service import EvalTaskService
from .crud import EvalTaskCRUD, EvalTaskCaseCRUD, EvalTaskResultCRUD, EvalTaskLogCRUD
from .tasks import run_eval_task
from app.api.v1.module_system.auth.schema import AuthSchema


EvalTaskRouter = APIRouter(
    route_class=OperationLogRoute, tags=["安全评测任务"]
)


@EvalTaskRouter.post("/tasks", summary="创建评测任务")
async def create_task_controller(
    data: EvalTaskCreateSchema,
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    """
    创建评测任务并投递到 Celery 队列执行
    
    参数:
    - data (EvalTaskCreateSchema): 创建任务的请求数据
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - SuccessResponse: 包含 task_id 的成功响应
    """
    service = EvalTaskService(db=db)
    task_id = await service.create_task(data=data)
    logger.info(f"创建评测任务成功: {task_id}，准备投递到 Celery 队列")
    
    # 投递任务到 Celery 队列，延迟1秒执行（等待数据库事务提交）
    run_eval_task.apply_async(args=[task_id], countdown=1)
    
    logger.info(f"评测任务已投递到 Celery 队列: {task_id}")
    return SuccessResponse(data={"task_id": task_id}, msg="创建评测任务成功")


@EvalTaskRouter.get("/tasks", summary="查询评测任务列表")
async def list_tasks_controller(
    page: PaginationQueryParam = Depends(),
    status: Optional[str] = Query(default=None, description="按状态过滤"),
    name: Optional[str] = Query(default=None, description="按名称模糊查询"),
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    """
    查询评测任务列表
    
    参数:
    - page (PaginationQueryParam): 分页查询参数模型
    - status (str | None): 按状态过滤
    - name (str | None): 按名称模糊查询
    - auth (AuthSchema): 认证信息模型
    
    返回:
    - SuccessResponse: 分页查询结果响应
    """
    crud = EvalTaskCRUD(auth)
    tasks = await crud.list_tasks(
        search={
            "status": status if status else None,
            "name": ("like", name) if name else None,
        },
        order_by=page.order_by,
    )
    # 转换为字典列表
    data_list = [
        {
            "id": t.id,
            "name": t.name,
            "status": t.status,
            "total_cases": t.total_cases,
            "finished_cases": t.finished_cases,
            "risk_summary": json.loads(t.risk_summary) if t.risk_summary else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "finished_at": t.finished_at.isoformat() if t.finished_at else None,
        }
        for t in tasks
    ]
    # 应用分页
    result_dict = await PaginationService.paginate(
        data_list=data_list,
        page_no=page.page_no,
        page_size=page.page_size
    )
    logger.info(f"查询评测任务列表成功")
    return SuccessResponse(data=result_dict, msg="查询评测任务列表成功")


@EvalTaskRouter.get("/tasks/{task_id}", summary="查询评测任务详情")
async def get_task_controller(
    task_id: int = Path(..., description="任务ID"),
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    task = await EvalTaskCRUD(auth).get_by_id(task_id)
    if not task:
        return SuccessResponse(data=None, msg="任务不存在", success=True)
    data = {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "total_cases": task.total_cases,
        "finished_cases": task.finished_cases,
        "risk_summary": json.loads(task.risk_summary) if task.risk_summary else None,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
    }
    return SuccessResponse(data=data, msg="查询评测任务详情成功")


@EvalTaskRouter.get("/tasks/{task_id}/cases", summary="查询评测任务用例列表")
async def get_task_cases_controller(
    task_id: int = Path(..., description="任务ID"),
    page: PaginationQueryParam = Depends(),
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
    request: Request = None,
) -> SuccessResponse:
    cases = await EvalTaskCaseCRUD(auth).list_cases(
        search={"task_id": task_id}, order_by=[{"id": "asc"}]
    )
    task = await EvalTaskCRUD(auth).get_by_id(task_id)
    status_val = task.status if task else None
    data_list = [
        {
            "id": c.id,
            "prompt": c.prompt,
            "status": c.status,
            "llm_provider": c.llm_provider,
            "llm_params": json.loads(c.llm_params) if c.llm_params else None,
            "output_text": c.output_text,
            "risk_scores": json.loads(c.risk_scores) if c.risk_scores else None,
            "risk_level": c.risk_level,
            "risk_reason": c.risk_reason,
            "completion_tokens": c.completion_tokens,
            "prompt_tokens": c.prompt_tokens,
            "total_tokens": c.total_tokens,
            "started_at": c.started_at.isoformat() if c.started_at else None,
            "finished_at": c.finished_at.isoformat() if c.finished_at else None,
        }
        for c in cases
    ]
    # 应用分页
    result_dict = await PaginationService.paginate(
        data_list=data_list,
        page_no=page.page_no,
        page_size=page.page_size
    )
    etag = f"W/\"cases:{task_id}:{status_val}:{page.page_no}:{page.page_size}\""
    if request and request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag})
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=300" if status_val in ("completed", "failed", "partial") else "no-store"
    }
    return SuccessResponse(data=result_dict, msg="查询评测任务用例列表成功", headers=headers)


@EvalTaskRouter.get("/tasks/{task_id}/result", summary="查询评测任务汇总结果")
async def get_task_result_controller(
    task_id: int = Path(..., description="任务ID"),
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    crud = EvalTaskResultCRUD(auth)
    obj = await crud.get(task_id=task_id)
    if not obj:
        return SuccessResponse(data=None, msg="任务结果不存在或未完成")
    summary = json.loads(obj.summary) if obj.summary else {}
    if isinstance(summary, dict):
        summary.pop("avg_scores", None)

    need_fields = {
        "total_cases",
        "succeeded_cases",
        "failed_cases",
        "qualified_cases",
        "qualified_rate",
        "level_distribution",
    }
    if not isinstance(summary, dict) or not need_fields.issubset(set(summary.keys())):
        task = await EvalTaskCRUD(auth).get_by_id(task_id)
        cases = await EvalTaskCaseCRUD(auth).list_cases(search={"task_id": task_id})

        total_cases = int(getattr(task, "total_cases", 0) or 0)
        finished_cases = int(getattr(task, "finished_cases", 0) or 0)
        succeeded_cases = sum(1 for c in cases if getattr(c, "status", None) == "succeeded")
        failed_cases = sum(1 for c in cases if getattr(c, "status", None) == "failed")
        if not finished_cases:
            finished_cases = int(succeeded_cases + failed_cases)

        level_distribution: dict[str, int] = {}
        qualified_cases = 0
        for c in cases:
            if getattr(c, "status", None) != "succeeded":
                continue
            lvl = getattr(c, "risk_level", None) or "Low"
            level_distribution[lvl] = level_distribution.get(lvl, 0) + 1
            if lvl == "Low":
                qualified_cases += 1

        qualified_rate = round((qualified_cases / total_cases) * 100, 2) if total_cases else 0.0
        summary = {
            "level_distribution": level_distribution,
            "total_cases": total_cases,
            "finished_cases": finished_cases,
            "succeeded_cases": int(succeeded_cases),
            "failed_cases": int(failed_cases),
            "qualified_cases": int(qualified_cases),
            "qualified_rate": qualified_rate,
        }
    data = {
        "task_id": task_id,
        "summary": summary,
        "metrics": json.loads(obj.metrics) if obj.metrics else {},
        "top_risks": json.loads(obj.top_risks) if obj.top_risks else [],
    }
    return SuccessResponse(data=data, msg="查询评测任务结果成功")


@EvalTaskRouter.get("/tasks/{task_id}/progress", summary="查询评测任务进度")
async def get_task_progress_controller(
    task_id: int = Path(..., description="任务ID"),
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
    request: Request = None,
) -> SuccessResponse:
    task = await EvalTaskCRUD(auth).get_by_id(task_id)
    if not task:
        return SuccessResponse(data=None, msg="任务不存在", success=True)
    percent = (
        round((task.finished_cases / task.total_cases) * 100, 2)
        if task.total_cases
        else 0.0
    )
    data = {
        "task_id": task.id,
        "status": task.status,
        "finished": task.finished_cases,
        "total": task.total_cases,
        "percent": percent,
        "polling": not (task.status in ("completed", "failed", "partial") or (task.total_cases and task.finished_cases >= task.total_cases)),
    }
    etag = f"W/\"progress:{task.id}:{task.finished_cases}:{task.status}\""
    if request and request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag})
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=300" if data["polling"] is False else "no-store",
    }
    if data["polling"]:
        headers["Retry-After"] = "2"
    return SuccessResponse(data=data, msg="查询评测任务进度成功", headers=headers)


@EvalTaskRouter.get("/tasks/{task_id}/logs", summary="查询评测任务执行日志")
async def get_task_logs_controller(
    task_id: int = Path(..., description="任务ID"),
    page: PaginationQueryParam = Depends(),
    stage: Optional[str] = Query(default=None, description="按阶段过滤"),
    level: Optional[str] = Query(default=None, description="按日志级别过滤"),
    case_id: Optional[int] = Query(default=None, description="按用例ID过滤"),
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    task = await EvalTaskCRUD(auth).get_by_id(task_id)
    if not task:
        return SuccessResponse(data=None, msg="任务不存在", success=True)

    search = {
        "task_id": task_id,
        "stage": stage if stage else None,
        "level": level if level else None,
        "case_id": case_id if case_id is not None else None,
    }
    logs = await EvalTaskLogCRUD(auth).list(search=search, order_by=page.order_by or [{"id": "desc"}])
    data_list = [
        {
            "id": x.id,
            "task_id": x.task_id,
            "case_id": x.case_id,
            "stage": x.stage,
            "level": x.level,
            "message": x.message,
            "created_at": x.created_at.isoformat() if x.created_at else None,
        }
        for x in logs
    ]
    result_dict = await PaginationService.paginate(
        data_list=data_list,
        page_no=page.page_no,
        page_size=page.page_size,
    )
    return SuccessResponse(data=result_dict, msg="查询评测任务执行日志成功")


@EvalTaskRouter.delete("/tasks", summary="删除评测任务")
async def delete_tasks_controller(
    ids: list[int] = Body(..., description="任务ID列表"),
    db: AsyncSession = Depends(db_getter),
    auth: AuthSchema = Depends(get_current_user),
) -> SuccessResponse:
    crud = EvalTaskCRUD(auth)
    count = await crud.delete_tasks(ids)
    logger.info(f"删除评测任务成功，数量: {count}")
    return SuccessResponse(data={"count": count}, msg=f"成功删除 {count} 个任务")
