# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from app.core.validator import DateTimeStr


class OnlineOutSchema(BaseModel):
    """
    在线用户对应pydantic模型
    """

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description='用户名称')
    session_id: str = Field(..., description='会话编号')
    user_id: int = Field(..., description='用户ID')
    user_name: str = Field(..., description='用户名')
    ipaddr: Optional[str] = Field(default=None, description='登陆IP地址')
    login_location: Optional[str] = Field(default=None, description='登录所属地')
    os: Optional[str] = Field(default=None, description='操作系统')
    browser: Optional[str] = Field(default=None, description='浏览器')
    login_time: Optional[DateTimeStr] = Field(default=None, description='登录时间')
    login_type: Optional[str] = Field(default=None, description='登录类型 PC端 | 移动端')
