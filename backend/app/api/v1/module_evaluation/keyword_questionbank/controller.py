# -*- coding: utf-8 -*-

from typing import List, Optional
from fastapi import APIRouter, Depends

from app.api.v1.module_evaluation.keyword_questionbank.param import KeywordQueryParam
from app.api.v1.module_evaluation.keyword_questionbank.schema import (
    KeywordCreateSchema, KeywordUpdateSchema,
    ImportKeywordSchema, KeywordMatchRequest
)
from app.api.v1.module_evaluation.keyword_questionbank.crud import KeywordCRUD
from app.api.v1.module_evaluation.keyword_questionbank.service import KeywordService
from app.core.base_crud import AuthSchema
from app.core.router_class import OperationLogRoute
from app.core.dependencies import AuthPermission
from app.common.response import SuccessResponse, StreamResponse
from app.common.request import PaginationService
from app.core.base_params import PaginationQueryParam
from app.utils.common_util import bytes2file_response
from app.core.logger import logger


# ==================== 关键词路由 ====================

KeywordRouter = APIRouter(prefix="/keyword", route_class=OperationLogRoute, tags=["关键词管理"])


def get_keyword_service(auth: AuthSchema = Depends(AuthPermission(["evaluation:keyword:list"]))):
    from app.api.v1.module_evaluation.keyword_questionbank.model import KeywordModel
    return KeywordService(KeywordCRUD(model=KeywordModel, auth=auth))


@KeywordRouter.post('/page', summary='分页查询关键词')
async def keyword_page_controller(
    page: PaginationQueryParam = Depends(),
    search: KeywordQueryParam = Depends(),
    service: KeywordService = Depends(get_keyword_service)
):
    result_list = list(await service.list(search=search.__dict__, order_by=page.order_by))
    result_dict = await PaginationService.paginate(data_list=result_list, page_no=page.page_no, page_size=page.page_size)
    return SuccessResponse(data=result_dict, msg='查询成功')


@KeywordRouter.post('/list', summary='获取关键词列表')
async def keyword_list_controller(
    search: KeywordQueryParam = Depends(),
    service: KeywordService = Depends(get_keyword_service)
):
    result_list = await service.list(search=search.__dict__)
    return SuccessResponse(data=result_list, msg='查询成功')


@KeywordRouter.get('/by-category/{category_id}', summary='获取某类别下的关键词')
async def keyword_by_category_controller(
    category_id: int,
    status: Optional[bool] = None,
    service: KeywordService = Depends(get_keyword_service)
):
    result = await service.get_by_category(category_id, status)
    return SuccessResponse(data=result, msg='查询成功')


@KeywordRouter.post('/create', summary='新增关键词', dependencies=[Depends(AuthPermission(["evaluation:keyword:create"]))])
async def keyword_create_controller(
    data: KeywordCreateSchema,
    service: KeywordService = Depends(get_keyword_service)
):
    result = await service.create(data)
    return SuccessResponse(data=result, msg='新增成功')


@KeywordRouter.post('/update/{id}', summary='更新关键词', dependencies=[Depends(AuthPermission(["evaluation:keyword:update"]))])
async def keyword_update_controller(
    id: int,
    data: KeywordUpdateSchema,
    service: KeywordService = Depends(get_keyword_service)
):
    result = await service.update(id, data)
    return SuccessResponse(data=result, msg='更新成功')


@KeywordRouter.post('/delete', summary='删除关键词', dependencies=[Depends(AuthPermission(["evaluation:keyword:delete"]))])
async def keyword_delete_controller(
    ids: List[int],
    service: KeywordService = Depends(get_keyword_service)
):
    await service.delete(ids)
    return SuccessResponse(msg='删除成功')


@KeywordRouter.post('/import', summary='批量导入关键词', dependencies=[Depends(AuthPermission(["evaluation:keyword:import"]))])
async def keyword_import_controller(
    payload: ImportKeywordSchema,
    service: KeywordService = Depends(get_keyword_service)
):
    result = await service.import_items(payload.items)
    return SuccessResponse(data=result, msg='导入完成')


@KeywordRouter.post('/export', summary='导出关键词', dependencies=[Depends(AuthPermission(["evaluation:keyword:export"]))])
async def keyword_export_controller(
    search: KeywordQueryParam = Depends(),
    service: KeywordService = Depends(get_keyword_service)
):
    keyword_list = await service.list(search=search.__dict__)
    export_result = await service.export_list(keyword_list)
    logger.info('导出关键词成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=keywords.xlsx'}
    )


@KeywordRouter.post('/match', summary='关键词匹配', dependencies=[Depends(AuthPermission(["evaluation:keyword:list"]))])
async def keyword_match_controller(
    request: KeywordMatchRequest,
    service: KeywordService = Depends(get_keyword_service)
):
    """
    对输入文本进行关键词匹配，返回匹配结果和风险评分
    """
    result = await service.match_keywords(request)
    return SuccessResponse(data=result.model_dump(), msg='匹配完成')


# ==================== 合并路由 ====================

KeywordQuestionBankRouter = APIRouter(prefix="/keyword-questionbank", tags=["关键词题库"])
KeywordQuestionBankRouter.include_router(KeywordRouter)
