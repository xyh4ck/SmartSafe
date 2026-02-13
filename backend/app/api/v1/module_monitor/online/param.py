# -*- coding: utf-8 -*-

from typing import Optional
from fastapi import Query


class OnlineQueryParam:
    """在线用户查询参数"""

    def __init__(
        self,
        name: Optional[str] = Query(None, description="登录名称"), 
        ipaddr: Optional[str] = Query(None, description="登陆IP地址"),
        login_location: Optional[str] = Query(None, description="登录所属地"),
    ) -> None:
        
        # 模糊查询字段
        self.name = ("like", f"%{name}%") if name else None
        self.login_location = ("like", f"%{login_location}%") if login_location else None
        self.ipaddr = ("like", f"%{ipaddr}%") if ipaddr else None

