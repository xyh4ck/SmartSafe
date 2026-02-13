# -*- coding: utf-8 -*-

"""
Celery 应用配置模块

用于创建和配置 Celery 实例，支持异步任务队列
"""

from celery import Celery
from kombu import Queue

from app.config.setting import settings


# 创建 Celery 实例
celery_app = Celery(
    "smartsafe",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.api.v1.module_evaltask.evaltask.tasks",  # 评测任务模块
    ],
)

# Celery 配置
celery_app.conf.update(
    # 序列化配置
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区配置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务配置
    task_track_started=True,  # 跟踪任务开始状态
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,  # 任务硬超时（秒）
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,  # 任务软超时（秒）
    
    # 结果配置
    result_expires=3600,  # 结果过期时间（秒）
    
    # Worker 配置
    worker_prefetch_multiplier=1,  # 每次只取一个任务，适合长任务
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,  # 并发数
    
    # 队列配置
    task_default_queue="default",
    task_queues=[
        Queue("default"),
        Queue("evaltask"),  # 评测任务专用队列
    ],
    
    # 重试配置
    task_acks_late=True,  # 任务完成后才确认，支持任务恢复
    task_reject_on_worker_lost=True,  # worker 丢失时拒绝任务，重新入队
    
    # Broker 连接重试配置（Celery 6.0 兼容）
    broker_connection_retry_on_startup=True,  # 启动时重试连接 broker
)

# 可选：配置任务路由（将特定任务路由到特定队列）
celery_app.conf.task_routes = {
    "app.api.v1.module_evaltask.evaltask.tasks.*": {"queue": "evaltask"},
}
