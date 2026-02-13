# -*- coding: utf-8 -*-

from typing import List, Optional
from fastapi import APIRouter, Depends

from app.api.v1.module_evaluation.testcase.param import TestCaseQueryParam
from app.api.v1.module_evaluation.testcase.schema import (
    TestCaseCreateSchema,
    TestCaseUpdateSchema,
    ImportTestCaseSchema,
)
from app.api.v1.module_evaluation.testcase.crud import TestCaseCRUD
from app.api.v1.module_evaluation.testcase.service import TestCaseService
from app.core.base_crud import AuthSchema
from app.core.router_class import OperationLogRoute
from app.core.dependencies import AuthPermission
from app.common.response import SuccessResponse, StreamResponse
from app.common.request import PaginationService
from app.core.base_params import PaginationQueryParam
from app.utils.common_util import bytes2file_response
from app.core.logger import logger


TestCaseRouter = APIRouter(prefix="/testcase", route_class=OperationLogRoute, tags=["测试用例管理"])


def get_service(auth: AuthSchema = Depends(AuthPermission(["evaluation:testcase:list"]))):
    return TestCaseService(TestCaseCRUD(model=__import__(
        'app.api.v1.module_evaluation.testcase.model', fromlist=['TestCaseModel']).TestCaseModel, auth=auth))


@TestCaseRouter.post('/page', summary='分页查询')
async def page_controller(
    page: PaginationQueryParam = Depends(),
    search: TestCaseQueryParam = Depends(),
    service: TestCaseService = Depends(get_service)
):
    result_list = list(await service.list(search=search.__dict__, order_by=page.order_by))
    result_dict = await PaginationService.paginate(data_list=result_list, page_no=page.page_no, page_size=page.page_size)
    return SuccessResponse(data=result_dict, msg='查询成功')


@TestCaseRouter.post('/create', summary='新增用例', dependencies=[Depends(AuthPermission(["evaluation:testcase:create"]))])
async def create_controller(data: TestCaseCreateSchema, service: TestCaseService = Depends(get_service)):
    result = await service.create(data)
    return SuccessResponse(data=result, msg='新增成功')


@TestCaseRouter.post('/update/{id}', summary='更新用例', dependencies=[Depends(AuthPermission(["evaluation:testcase:update"]))])
async def update_controller(id: int, data: TestCaseUpdateSchema, service: TestCaseService = Depends(get_service)):
    result = await service.update(id, data)
    return SuccessResponse(data=result, msg='更新成功')


@TestCaseRouter.post('/delete', summary='删除用例', dependencies=[Depends(AuthPermission(["evaluation:testcase:delete"]))])
async def delete_controller(ids: List[int], service: TestCaseService = Depends(get_service)):
    await service.delete(ids)
    return SuccessResponse(msg='删除成功')


@TestCaseRouter.post('/import', summary='批量导入', dependencies=[Depends(AuthPermission(["evaluation:testcase:import"]))])
async def import_controller(payload: ImportTestCaseSchema, service: TestCaseService = Depends(get_service)):
    result = await service.import_items(payload.items)
    return SuccessResponse(data=result, msg='导入完成')


@TestCaseRouter.post('/export', summary='导出列表', dependencies=[Depends(AuthPermission(["evaluation:testcase:export"]))])
async def export_controller(
    search: TestCaseQueryParam = Depends(),
    service: TestCaseService = Depends(get_service)
):
    """
    导出测试用例列表
    
    参数:
    - search (TestCaseQueryParam): 查询参数模型
    
    返回:
    - StreamingResponse: 测试用例导出Excel文件流响应
    """
    testcase_list = await service.list(search=search.__dict__)
    testcase_export_result = await service.export_testcase_list_service(testcase_list)
    logger.info('导出测试用例成功')

    return StreamResponse(
        data=bytes2file_response(testcase_export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment; filename=testcase.xlsx'
        }
    )


