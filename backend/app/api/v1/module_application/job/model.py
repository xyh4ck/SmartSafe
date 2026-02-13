# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import CreatorMixin, MappedBase


class JobModel(CreatorMixin):
    """
    定时任务调度表
    """
    __tablename__ = 'app_job'
    __table_args__ = ({'comment': '定时任务调度表'})
    __loader_options__ = ["job_logs", "creator"]

    name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default='', comment='任务名称')
    jobstore: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default='default', comment='存储器')
    executor: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default='default', comment='执行器:将运行此作业的执行程序的名称')
    trigger: Mapped[str] = mapped_column(String(64), nullable=False, comment='触发器:控制此作业计划的 trigger 对象')
    trigger_args: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='触发器参数')
    func: Mapped[str] = mapped_column(Text, nullable=False, comment='任务函数')
    args: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='位置参数')
    kwargs: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='关键字参数')
    coalesce: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False, comment='是否合并运行:是否在多个运行时间到期时仅运行作业一次')
    max_instances: Mapped[int] = mapped_column(Integer, nullable=True, default=1, comment='最大实例数:允许的最大并发执行实例数 工作')
    start_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment='开始时间')
    end_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment='结束时间')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    job_logs: Mapped[Optional[list['JobLogModel']]] = relationship(back_populates="job", lazy="selectin")


class JobLogModel(MappedBase):
    """
    定时任务调度日志表
    """
    __tablename__ = 'app_job_log'
    __table_args__ = ({'comment': '定时任务调度日志表'})
    __loader_options__ = ["job"]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    job_name: Mapped[str] = mapped_column(String(64),nullable=False,comment='任务名称')
    job_group: Mapped[str] = mapped_column(String(64),nullable=False,comment='任务组名')
    job_executor: Mapped[str] = mapped_column(String(64),nullable=False,comment='任务执行器')
    invoke_target: Mapped[str] = mapped_column(String(500),nullable=False,comment='调用目标字符串')
    job_args: Mapped[Optional[str]] = mapped_column(String(255),nullable=True,default='',comment='位置参数')
    job_kwargs: Mapped[Optional[str]] = mapped_column(String(255),nullable=True,default='',comment='关键字参数')
    job_trigger: Mapped[Optional[str]] = mapped_column(String(255),nullable=True,default='',comment='任务触发器')
    job_message: Mapped[Optional[str]] = mapped_column(String(500),nullable=True,default='',comment='日志信息')
    exception_info: Mapped[Optional[str]] = mapped_column(String(2000),nullable=True,default='',comment='异常信息')
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey('app_job.id'), comment='任务ID')
    status: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, comment="是否启用(True:启用 False:禁用)")
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    # 任务关联关系
    job: Mapped[Optional["JobModel"]] = relationship(back_populates="job_logs", lazy="selectin")