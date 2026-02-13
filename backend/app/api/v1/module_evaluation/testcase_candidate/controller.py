# -*- coding: utf-8 -*-

from typing import List
from fastapi import APIRouter, Depends

from app.api.v1.module_evaluation.testcase_candidate.param import TestCaseCandidateQueryParam
from app.api.v1.module_evaluation.testcase_candidate.schema import (
    TestCaseCandidateCreateSchema,
    BatchReviewSchema,
    BatchPublishSchema,
    GenerateCandidateSchema,
)
from app.api.v1.module_evaluation.testcase_candidate.crud import TestCaseCandidateCRUD
from app.api.v1.module_evaluation.testcase_candidate.service import TestCaseCandidateService
from app.core.base_crud import AuthSchema
from app.core.router_class import OperationLogRoute
from app.core.dependencies import AuthPermission
from app.common.response import SuccessResponse
from app.common.request import PaginationService
from app.core.base_params import PaginationQueryParam
from app.core.logger import logger


TestCaseCandidateRouter = APIRouter(prefix="/testcase-candidate", route_class=OperationLogRoute, tags=["候选题池管理"])


def get_service(auth: AuthSchema = Depends(AuthPermission(["evaluation:testcase:list"]))):
    return TestCaseCandidateService(TestCaseCandidateCRUD(model=__import__(
        'app.api.v1.module_evaluation.testcase_candidate.model', fromlist=['TestCaseCandidateModel']).TestCaseCandidateModel, auth=auth))


@TestCaseCandidateRouter.post('/page', summary='分页查询候选题')
async def page_controller(
    page: PaginationQueryParam = Depends(),
    search: TestCaseCandidateQueryParam = Depends(),
    service: TestCaseCandidateService = Depends(get_service)
):
    result_list = list(await service.list(search=search.__dict__, order_by=page.order_by))
    result_dict = await PaginationService.paginate(data_list=result_list, page_no=page.page_no, page_size=page.page_size)
    return SuccessResponse(data=result_dict, msg='查询成功')


@TestCaseCandidateRouter.post('/create', summary='新增候选题', dependencies=[Depends(AuthPermission(["evaluation:testcase:create"]))])
async def create_controller(data: TestCaseCandidateCreateSchema, service: TestCaseCandidateService = Depends(get_service)):
    result = await service.create(data)
    return SuccessResponse(data=result, msg='新增成功')


@TestCaseCandidateRouter.post('/review', summary='批量审核候选题', dependencies=[Depends(AuthPermission(["evaluation:testcase:update"]))])
async def review_controller(
    data: BatchReviewSchema,
    service: TestCaseCandidateService = Depends(get_service),
    auth: AuthSchema = Depends(AuthPermission(["evaluation:testcase:update"]))
):
    result = await service.batch_review(data.ids, data.action, auth.user.id, data.review_note)
    return SuccessResponse(data=result, msg='审核完成')


@TestCaseCandidateRouter.post('/publish', summary='发布候选题到正式库', dependencies=[Depends(AuthPermission(["evaluation:testcase:create"]))])
async def publish_controller(data: BatchPublishSchema, service: TestCaseCandidateService = Depends(get_service)):
    result = await service.publish(data.ids)
    return SuccessResponse(data=result, msg='发布完成')


@TestCaseCandidateRouter.post('/generate', summary='自动生成候选题', dependencies=[Depends(AuthPermission(["evaluation:testcase:create"]))])
async def generate_controller(data: GenerateCandidateSchema, service: TestCaseCandidateService = Depends(get_service)):
    result = await service.generate_candidates(
        refusal_expectation=data.refusal_expectation,
        category_ids=data.category_ids,
        count_per_category=data.count_per_category,
    )
    return SuccessResponse(data=result, msg='生成完成')


@TestCaseCandidateRouter.get('/coverage', summary='获取题库覆盖度统计')
async def coverage_controller(service: TestCaseCandidateService = Depends(get_service)):
    result = await service.get_coverage()
    return SuccessResponse(data=result, msg='查询成功')


@TestCaseCandidateRouter.post('/delete', summary='删除候选题', dependencies=[Depends(AuthPermission(["evaluation:testcase:delete"]))])
async def delete_controller(ids: List[int], service: TestCaseCandidateService = Depends(get_service)):
    await service.crud.delete_crud(ids)
    return SuccessResponse(msg='删除成功')
