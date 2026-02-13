# -*- coding: utf-8 -*-

import io
import pandas as pd
from typing import List, Optional
from urllib.parse import quote
from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.api.v1.module_evaluation.category.schema import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
from app.api.v1.module_evaluation.category.crud import CategoryCRUD
from app.api.v1.module_evaluation.category.service import CategoryService
from app.api.v1.module_evaluation.dimension.model import DimensionModel
from app.core.base_crud import AuthSchema
from app.core.router_class import OperationLogRoute
from app.core.dependencies import AuthPermission
from app.common.response import SuccessResponse
from app.common.request import PaginationService
from app.core.base_params import PaginationQueryParam
from app.utils.excel_util import ExcelUtil
from app.core.logger import logger


CategoryRouter = APIRouter(
    prefix="/category", route_class=OperationLogRoute, tags=["测试用例分类管理"]
)


def get_service(
    auth: AuthSchema = Depends(AuthPermission(["evaluation:category:list"])),
):
    return CategoryService(
        CategoryCRUD(
            model=__import__(
                "app.api.v1.module_evaluation.category.model",
                fromlist=["CategoryModel"],
            ).CategoryModel,
            auth=auth,
        )
    )


@CategoryRouter.post("/page", summary="分页查询")
async def page_controller(
    page: PaginationQueryParam = Depends(),
    service: CategoryService = Depends(get_service),
):
    search = {}
    result_list = list(await service.list(search=search, order_by=page.order_by))
    result_dict = await PaginationService.paginate(
        data_list=result_list, page_no=page.page_no, page_size=page.page_size
    )
    return SuccessResponse(data=result_dict, msg="查询成功")


@CategoryRouter.get("/list", summary="获取列表")
async def list_controller(service: CategoryService = Depends(get_service)):
    result_list = await service.list()
    return SuccessResponse(data=result_list, msg="查询成功")


@CategoryRouter.get("/by-dimension", summary="根据维度获取分类")
async def get_by_dimension_controller(
    dimension_id: int = Query(..., description="维度ID"),
    only_active: bool = Query(default=False, description="仅启用"),
    service: CategoryService = Depends(get_service),
):
    result_list = await service.get_by_dimension(dimension_id, only_active)
    return SuccessResponse(data=result_list, msg="查询成功")


@CategoryRouter.get("/tree", summary="获取维度-分类树形结构")
async def get_tree_controller(
    only_active: bool = Query(default=False, description="仅启用"),
    service: CategoryService = Depends(get_service),
):
    """
    一次性获取所有维度及其分类的树形结构
    返回格式: [{ dimension_id, dimension_name, categories: [...] }]
    """
    result_tree = await service.get_dimension_category_tree(only_active)
    return SuccessResponse(data=result_tree, msg="查询成功")


@CategoryRouter.post(
    "/create",
    summary="新增分类",
    dependencies=[Depends(AuthPermission(["evaluation:category:create"]))],
)
async def create_controller(
    data: CategoryCreateSchema, service: CategoryService = Depends(get_service)
):
    result = await service.create(data)
    return SuccessResponse(data=result, msg="新增成功")


@CategoryRouter.post(
    "/update/{id}",
    summary="更新分类",
    dependencies=[Depends(AuthPermission(["evaluation:category:update"]))],
)
async def update_controller(
    id: int, data: CategoryUpdateSchema, service: CategoryService = Depends(get_service)
):
    result = await service.update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@CategoryRouter.post(
    "/delete",
    summary="删除分类",
    dependencies=[Depends(AuthPermission(["evaluation:category:delete"]))],
)
async def delete_controller(
    ids: List[int], service: CategoryService = Depends(get_service)
):
    await service.delete(ids)
    return SuccessResponse(msg="删除成功")


@CategoryRouter.get(
    "/export-template",
    summary="导出导入模板",
    dependencies=[Depends(AuthPermission(["evaluation:category:export"]))],
)
async def export_template_controller():
    """
    导出分类导入模板
    """
    try:
        header_list = ["维度名称", "分类名称", "分类代码", "排序", "是否启用", "备注"]
        selector_header_list = ["是否启用"]
        option_list = [{"是否启用": ["是", "否"]}]

        excel_data = ExcelUtil.get_excel_template(
            header_list, selector_header_list, option_list
        )

        # 构建响应
        response = StreamingResponse(
            iter([excel_data]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        # 使用 RFC 5987 编码中文文件名
        filename = quote("分类导入模板.xlsx".encode("utf-8"), safe="")
        response.headers["Content-Disposition"] = (
            f"attachment; filename*=UTF-8''{filename}"
        )
        return response
    except Exception as e:
        logger.error(f"导出模板失败: {str(e)}")
        return SuccessResponse(msg=f"导出模板失败: {str(e)}", code=500)


@CategoryRouter.post(
    "/export",
    summary="导出分类数据",
    dependencies=[Depends(AuthPermission(["evaluation:category:export"]))],
)
async def export_controller(service: CategoryService = Depends(get_service)):
    """
    导出所有分类数据
    """
    try:
        result_list = await service.list()

        # 将模型对象转换为字典，只保留需要的字段
        export_data = []
        for item in result_list:
            if hasattr(item, "__dict__"):
                dim_obj = getattr(item, "dimension", None)
                dim_name = getattr(dim_obj, "name", None) if dim_obj else None
                data_dict = {
                    "dimension_name": dim_name,
                    "name": getattr(item, "name", ""),
                    "code": getattr(item, "code", None),
                    "sort": getattr(item, "sort", 0),
                    "status": getattr(item, "status", True),
                    "description": getattr(item, "description", None),
                }
            else:
                dim = item.get("dimension")
                dim_name = dim.get("name") if isinstance(dim, dict) else None
                data_dict = {
                    "dimension_name": dim_name,
                    "name": item.get("name", ""),
                    "code": item.get("code"),
                    "sort": item.get("sort", 0),
                    "status": item.get("status", True),
                    "description": item.get("description"),
                }

            # 转换布尔值为是否
            if isinstance(data_dict.get("status"), bool):
                data_dict["status"] = "是" if data_dict["status"] else "否"
            elif isinstance(data_dict.get("status"), str):
                # 如果已经是字符串，保持不变
                pass

            export_data.append(data_dict)

        # 排序：按维度名称，其次按分类排序值与名称
        export_data.sort(
            key=lambda d: (
                (d.get("dimension_name") or ""),
                d.get("sort", 0),
                (d.get("name") or ""),
            )
        )

        # 字段映射
        mapping_dict = {
            "dimension_name": "维度名称",
            "name": "分类名称",
            "code": "分类代码",
            "sort": "排序",
            "status": "是否启用",
            "description": "备注",
        }

        excel_data = ExcelUtil.export_list2excel(export_data, mapping_dict)

        # 构建响应
        response = StreamingResponse(
            iter([excel_data]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        # 使用 RFC 5987 编码中文文件名
        filename = quote("风险分类数据.xlsx".encode("utf-8"), safe="")
        response.headers["Content-Disposition"] = (
            f"attachment; filename*=UTF-8''{filename}"
        )
        return response
    except Exception as e:
        logger.error(f"导出数据失败: {str(e)}")
        return SuccessResponse(msg=f"导出数据失败: {str(e)}", code=500)


@CategoryRouter.post(
    "/import",
    summary="导入分类数据",
    dependencies=[Depends(AuthPermission(["evaluation:category:import"]))],
)
async def import_controller(
    file: UploadFile = File(...), service: CategoryService = Depends(get_service)
):
    """
    导入分类数据
    """
    try:
        # 读取上传的文件
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        # 转换数据
        import_data = []
        for idx, row in df.iterrows():
            # 跳过空行
            if pd.isna(row.get("分类名称")):
                continue

            # 转换布尔值
            status = True
            if isinstance(row.get("是否启用"), str):
                status = row.get("是否启用") in ["是", "true", "True"]

            import_data.append(
                {
                    "dimension_name": (
                        str(row.get("维度名称", "")).strip()
                        if pd.notna(row.get("维度名称"))
                        else ""
                    ),
                    "name": str(row.get("分类名称", "")).strip(),
                    "code": (
                        str(row.get("分类代码", "")).strip()
                        if pd.notna(row.get("分类代码"))
                        else None
                    ),
                    "sort": int(row.get("排序", 0)) if pd.notna(row.get("排序")) else 0,
                    "status": status,
                    "description": (
                        str(row.get("备注", "")).strip()
                        if pd.notna(row.get("备注"))
                        else None
                    ),
                }
            )

        # 批量导入
        success_count = 0
        error_list = []

        for item in import_data:
            try:
                if not item["name"]:
                    error_list.append("分类名称不能为空")
                    continue
                if not item.get("dimension_name"):
                    error_list.append("维度名称不能为空")
                    continue
                dim = await service.db.scalar(
                    select(DimensionModel).where(
                        DimensionModel.name == item["dimension_name"]
                    )
                )
                if not dim:
                    error_list.append(f"维度 '{item['dimension_name']}' 不存在")
                    continue
                payload = {
                    "dimension_id": dim.id,
                    "name": item["name"],
                    "code": item.get("code"),
                    "sort": item.get("sort", 0),
                    "status": item.get("status", True),
                    "description": item.get("description"),
                }
                schema = CategoryCreateSchema(**payload)
                await service.create(schema)
                success_count += 1
            except Exception as e:
                error_list.append(f"第 {idx + 1} 行: {str(e)}")

        return SuccessResponse(
            data={
                "success_count": success_count,
                "error_count": len(error_list),
                "errors": error_list,
            },
            msg=f"导入成功 {success_count} 条，失败 {len(error_list)} 条",
        )
    except Exception as e:
        logger.error(f"导入数据失败: {str(e)}")
        return SuccessResponse(msg=f"导入数据失败: {str(e)}", code=500)
