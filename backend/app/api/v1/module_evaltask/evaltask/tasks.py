# -*- coding: utf-8 -*-

"""
评测任务 Celery 任务模块

定义评测任务的异步执行逻辑

注意：为避免循环导入，所有 app 模块的导入都放在函数内部
"""

import asyncio
import logging
from celery.exceptions import SoftTimeLimitExceeded

from app.core.celery_app import celery_app

# 使用标准 logging 而非 app.core.logger，避免循环导入
celery_logger = logging.getLogger("celery.task.evaltask")


@celery_app.task(
    bind=True,
    name="module_evaltask.run_eval_task",
    queue="evaltask",
    max_retries=3,
    default_retry_delay=60,  # 重试间隔60秒
    autoretry_for=(Exception,),
    retry_backoff=True,  # 指数退避
    retry_backoff_max=600,  # 最大退避时间10分钟
    acks_late=True,
)
def run_eval_task(self, task_id: int):
    """
    执行评测任务的 Celery 任务
    
    参数:
    - task_id (int): 评测任务ID
    
    该任务会：
    1. 检查任务状态，防止重复执行
    2. 调用 EvalTaskService.run_task() 执行评测
    3. 异常时更新任务状态为 failed
    """
    celery_logger.info(f"[Celery] 开始执行评测任务: {task_id}, retry={self.request.retries}")
    
    # 在同步任务中运行异步代码
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(_run_eval_task_async(task_id))
        celery_logger.info(f"[Celery] 评测任务执行成功: {task_id}")
    except SoftTimeLimitExceeded:
        celery_logger.error(f"[Celery] 评测任务软超时: {task_id}")
        loop.run_until_complete(_update_task_status_failed(task_id, "任务执行超时"))
        raise
    except Exception as e:
        celery_logger.error(f"[Celery] 评测任务执行失败: {task_id}, 错误: {str(e)}", exc_info=True)
        # 如果已经是最后一次重试，更新状态为失败
        if self.request.retries >= self.max_retries:
            loop.run_until_complete(_update_task_status_failed(task_id, str(e)))
        raise
    finally:
        loop.close()


async def _run_eval_task_async(task_id: int):
    """
    异步执行评测任务
    
    参数:
    - task_id (int): 评测任务ID
    """
    from app.core.database import AsyncSessionLocal
    from app.api.v1.module_evaltask.evaltask.service import EvalTaskService
    from app.api.v1.module_evaltask.evaltask.crud import EvalTaskCRUD
    from app.api.v1.module_system.auth.schema import AuthSchema
    
    async with AsyncSessionLocal() as db:
        try:
            # 幂等检查：获取任务状态，防止重复执行
            auth = AuthSchema(db=db)
            task_crud = EvalTaskCRUD(auth)
            task = await task_crud.get_by_id(task_id)
            
            if not task:
                celery_logger.error(f"[Celery] 任务不存在: {task_id}")
                return
            
            # 如果任务已经在运行中或已终态（completed/failed/partial），跳过执行
            if task.status in ("running", "completed", "failed", "partial"):
                celery_logger.warning(f"[Celery] 任务 {task_id} 状态为 {task.status}，跳过执行")
                return
            
            # 执行任务
            service = EvalTaskService(db=db)
            await service.run_task(task_id)
            
        except Exception as e:
            celery_logger.error(f"[Celery] 异步执行评测任务失败: {task_id}, 错误: {str(e)}", exc_info=True)
            raise
        finally:
            await db.close()


async def _update_task_status_failed(task_id: int, error_msg: str = ""):
    """
    更新任务状态为失败
    
    参数:
    - task_id (int): 评测任务ID
    - error_msg (str): 错误信息
    """
    from app.core.database import AsyncSessionLocal
    from app.api.v1.module_evaltask.evaltask.crud import EvalTaskCRUD
    from app.api.v1.module_system.auth.schema import AuthSchema
    
    try:
        async with AsyncSessionLocal() as db:
            auth = AuthSchema(db=db)
            task_crud = EvalTaskCRUD(auth)
            await task_crud.update_task(task_id, {"status": "failed"})
            await db.commit()
            celery_logger.info(f"[Celery] 任务 {task_id} 状态已更新为失败: {error_msg}")
    except Exception as e:
        celery_logger.error(f"[Celery] 更新任务状态失败: {task_id}, 错误: {str(e)}", exc_info=True)
