# -*- coding: utf-8 -*-

import time
from typing import List
from fastapi import APIRouter, Depends

from app.api.v1.module_evaluation.dimension.schema import (
    DimensionCreateSchema,
    DimensionUpdateSchema,
)
from app.api.v1.module_evaluation.dimension.service import DimensionService
from app.api.v1.module_evaluation.dimension.param import DimensionQueryParam
from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.router_class import OperationLogRoute
from app.core.dependencies import AuthPermission
from app.common.response import SuccessResponse, JSONResponse
from app.core.base_params import PaginationQueryParam
from app.core.logger import logger


DimensionRouter = APIRouter(
    prefix="/dimension", route_class=OperationLogRoute, tags=["测试用例维度管理"]
)


@DimensionRouter.get("/list", summary="查询维度", description="查询维度")
async def get_obj_list_controller(
    page: PaginationQueryParam = Depends(),
    search: DimensionQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["evaluation:dimension:list"])),
) -> JSONResponse:
    """
    查询维度（分页）

    参数:
    - page (PaginationQueryParam): 分页查询参数模型
    - search (DimensionQueryParam): 查询参数模型
    - auth (AuthSchema): 认证信息模型

    返回:
    - SuccessResponse: 分页查询结果响应
    """
    # 兼容历史行为：不传分页参数时返回全部；传入分页参数时走 DB 层分页避免全量查询
    if page.page_no is not None and page.page_size is not None:
        result_dict = await DimensionService.get_dimension_page_service(
            auth=auth,
            page_no=page.page_no,
            page_size=page.page_size,
            search=search.__dict__,
            order_by=page.order_by,
        )
    else:
        result_list = await DimensionService.get_dimension_list_service(
            auth=auth, search=search.__dict__, order_by=page.order_by
        )
        result_dict = {"items": result_list, "total": len(result_list), "page_no": None, "page_size": None, "has_next": False}
    logger.info("查询维度成功")
    return SuccessResponse(data=result_dict, msg="查询维度成功")


@DimensionRouter.post("/page", summary="分页查询", description="分页查询（兼容旧接口）")
async def page_controller(
    page: PaginationQueryParam = Depends(),
    search: DimensionQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["evaluation:dimension:list"])),
) -> JSONResponse:
    """
    分页查询（兼容旧接口，推荐使用 GET /list）

    参数:
    - page (PaginationQueryParam): 分页查询参数模型
    - search (DimensionQueryParam): 查询参数模型
    - auth (AuthSchema): 认证信息模型

    返回:
    - SuccessResponse: 分页查询结果响应
    """
    # 旧接口兼容：默认按第一页/每页10条分页
    page_no = page.page_no or 1
    page_size = page.page_size or 10
    result_dict = await DimensionService.get_dimension_page_service(
        auth=auth,
        page_no=page_no,
        page_size=page_size,
        search=search.__dict__,
        order_by=page.order_by,
    )
    logger.info("查询维度成功")
    return SuccessResponse(data=result_dict, msg="查询维度成功")


@DimensionRouter.get("/all-active", summary="获取所有启用的维度")
async def all_active_controller(
    auth: AuthSchema = Depends(AuthPermission(["evaluation:dimension:list"])),
):
    """
    获取所有启用的维度（用于下拉选择）

    参数:
    - auth (AuthSchema): 认证信息模型

    返回:
    - SuccessResponse: 启用的维度列表
    """
    result_list = await DimensionService.get_all_active_dimension_service(auth=auth)
    return SuccessResponse(data=result_list, msg="查询成功")


@DimensionRouter.post(
    "/create",
    summary="新增维度",
    dependencies=[Depends(AuthPermission(["evaluation:dimension:create"]))],
)
async def create_controller(
    data: DimensionCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["evaluation:dimension:create"])),
):
    """
    新增维度

    参数:
    - data (DimensionCreateSchema): 维度创建信息
    - auth (AuthSchema): 认证信息模型

    返回:
    - SuccessResponse: 创建结果响应
    """
    result = await DimensionService.create_dimension_service(auth=auth, data=data)
    return SuccessResponse(data=result, msg="新增成功")


@DimensionRouter.post(
    "/update/{id}",
    summary="更新维度",
    dependencies=[Depends(AuthPermission(["evaluation:dimension:update"]))],
)
async def update_controller(
    id: int,
    data: DimensionUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["evaluation:dimension:update"])),
):
    """
    更新维度

    参数:
    - id (int): 维度ID
    - data (DimensionUpdateSchema): 维度更新信息
    - auth (AuthSchema): 认证信息模型

    返回:
    - SuccessResponse: 更新结果响应
    """
    result = await DimensionService.update_dimension_service(
        auth=auth, id=id, data=data
    )
    return SuccessResponse(data=result, msg="更新成功")


@DimensionRouter.post(
    "/delete",
    summary="删除维度",
    dependencies=[Depends(AuthPermission(["evaluation:dimension:delete"]))],
)
async def delete_controller(
    ids: List[int],
    auth: AuthSchema = Depends(AuthPermission(["evaluation:dimension:delete"])),
):
    """
    删除维度

    参数:
    - ids (List[int]): 维度ID列表
    - auth (AuthSchema): 认证信息模型

    返回:
    - SuccessResponse: 删除结果响应
    """
    await DimensionService.delete_dimension_service(auth=auth, ids=ids)
    return SuccessResponse(msg="删除成功")
