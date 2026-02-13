# -*- coding: utf-8 -*-

import time
import json
from typing import Any
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.common.response import ErrorResponse
from app.config.setting import settings
from app.core.logger import logger
from app.core.exceptions import CustomException
from app.api.v1.module_system.params.service import ParamsService


class CustomCORSMiddleware(CORSMiddleware):
    """CORS跨域中间件"""
    def __init__(self, app: ASGIApp) -> None:
        CORSMiddlewareConfig: dict[str, Any]    = {
            "allow_origins": settings.ALLOW_ORIGINS,
            "allow_methods": settings.ALLOW_METHODS,
            "allow_headers": settings.ALLOW_HEADERS,
            "allow_credentials": settings.ALLOW_CREDENTIALS,
            "expose_headers": settings.CORS_EXPOSE_HEADERS,
        }
        super().__init__(app, **CORSMiddlewareConfig)


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    记录请求日志中间件: 提供一个基础的中间件类，允许你自定义请求和响应处理逻辑。
    """
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        # 构建请求日志信息
        request_info = f"请求方法: {request.method}, 请求路径: {request.url.path}"
        if request.client:
            request_info = f"请求来源: {request.client.host}, {request_info}"
        logger.info(request_info)

        try:
            # 初始化响应变量
            response = None
            
            # 获取请求路径
            path = request.scope.get("path")
            
            # 尝试获取客户端真实IP
            request_ip = None
            x_forwarded_for = request.headers.get('X-Forwarded-For')
            if x_forwarded_for:
                # 取第一个 IP 地址，通常为客户端真实 IP
                request_ip = x_forwarded_for.split(',')[0].strip()
            else:
                # 若没有 X-Forwarded-For 头，则使用 request.client.host
                request_ip = request.client.host if request.client else None
            
            # 检查是否启用演示模式
            demo_enable = False
            ip_white_list = []
            white_api_list_path = []
            ip_black_list = []
            
            try:
                # 从应用实例获取Redis连接
                redis = request.app.state.redis
                if not redis:
                    raise Exception("无法获取Redis连接")
                
                # 使用ParamsService获取系统配置
                system_config = await ParamsService.get_system_config_for_middleware(redis)
                # 提取配置值
                demo_enable = system_config["demo_enable"]
                ip_white_list = system_config["ip_white_list"]
                white_api_list_path = system_config["white_api_list_path"]
                ip_black_list = system_config["ip_black_list"]
                
            except Exception as e:
                logger.warning(f"获取系统配置失败: {e}")
            
            # 检查是否需要拦截请求
            should_block = False
            
            # 1. 首先检查IP是否在黑名单中
            if request_ip and request_ip in ip_black_list:
                should_block = True
            
            # 2. 如果不在黑名单中，检查是否在演示模式下需要拦截
            elif demo_enable in ["true", "True"] and request.method != "GET":
                # 在演示模式下，非GET请求需要检查白名单
                is_ip_whitelisted = request_ip in ip_white_list
                is_path_whitelisted = path in white_api_list_path
                
                if not is_ip_whitelisted and not is_path_whitelisted:
                    should_block = True
            
            if should_block:
                # 拦截请求
                return ErrorResponse(msg="演示环境，禁止操作")
            else:
                # 正常处理请求
                response = await call_next(request)
            
            # 计算处理时间并添加到响应头
            process_time = round(time.time() - start_time, 5)
            response.headers["X-Process-Time"] = str(process_time)
            
            # 构建响应日志信息
            session_id = request.scope.get('session_id')
            user_id = request.scope.get('user_id')
            
            # 构建用户信息字符串
            if session_id:
                user_info = f"会话ID: {session_id}"
                if user_id:
                    user_info += f", 用户ID: {user_id}"
            else:
                user_info = "未认证请求"
            
            content_length = response.headers.get('content-length', '0')
            response_info = (
                f"{user_info}, "
                f"响应状态: {response.status_code}, "
                f"响应内容长度: {content_length}, "
                f"处理时间: {process_time}s"
            )
            logger.info(response_info)
            
            return response
        
        except CustomException as e:
            logger.error(f"中间件处理异常: {str(e)}")
            return ErrorResponse(msg=f"系统异常，请联系管理员", data=str(e))


class CustomGZipMiddleware(GZipMiddleware):
    """GZip压缩中间件"""
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(
            app,
            minimum_size=settings.GZIP_MIN_SIZE,
            compresslevel=settings.GZIP_COMPRESS_LEVEL
        )

