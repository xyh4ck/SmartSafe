from typing import List
from fastapi import APIRouter, Depends, Path, Body
from fastapi.responses import JSONResponse

from app.common.response import SuccessResponse
from app.common.request import PaginationService
from app.core.base_params import PaginationQueryParam
from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute
from app.api.v1.module_system.auth.schema import AuthSchema
from .param import ModelRegistryQueryParam
from .service import ModelRegistryService
from .schema import ModelRegistryCreateSchema, ModelRegistryUpdateSchema


ModelRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/registry", tags=["模型接入管理"]
)


@ModelRouter.get("/detail/{id}")
async def detail_controller(
    id: int = Path(...),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:query"])),
) -> JSONResponse:
    result = await ModelRegistryService.detail_service(auth=auth, id=id)
    return SuccessResponse(data=result, msg="获取成功")


@ModelRouter.get("/list")
async def list_controller(
    page: PaginationQueryParam = Depends(),
    search: ModelRegistryQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:query"])),
) -> JSONResponse:
    result_list = await ModelRegistryService.list_service(
        auth=auth, search=search.__dict__, order_by=page.order_by
    )
    result = await PaginationService.paginate(
        data_list=result_list, page_no=page.page_no, page_size=page.page_size
    )
    return SuccessResponse(data=result, msg="查询成功")


@ModelRouter.post("/create")
async def create_controller(
    data: ModelRegistryCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:create"])),
) -> JSONResponse:
    result = await ModelRegistryService.create_service(auth=auth, data=data)
    return SuccessResponse(data=result, msg="创建成功")


@ModelRouter.put("/update/{id}")
async def update_controller(
    data: ModelRegistryUpdateSchema,
    id: int = Path(...),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:update"])),
) -> JSONResponse:
    result = await ModelRegistryService.update_service(auth=auth, id=id, data=data)
    return SuccessResponse(data=result, msg="修改成功")


@ModelRouter.delete("/delete")
async def delete_controller(
    ids: List[int] = Body(...),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:delete"])),
) -> JSONResponse:
    await ModelRegistryService.delete_service(auth=auth, ids=ids)
    return SuccessResponse(msg="删除成功")


@ModelRouter.post("/connect/test/{id}")
async def connectivity_test_controller(
    id: int = Path(...),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:test"])),
) -> JSONResponse:
    result = await ModelRegistryService.connectivity_test_service(auth=auth, id=id)
    return SuccessResponse(data=result, msg='连通性测试成功')


@ModelRouter.patch("/available/setting")
async def batch_available_controller(
    body: dict = Body(...),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:available"])),
) -> JSONResponse:
    ids = body.get("ids") or []
    status = body.get("status")
    await ModelRegistryService.batch_available_service(
        auth=auth, ids=ids, status=bool(status)
    )
    return SuccessResponse(msg="设置成功")


@ModelRouter.put("/version/{id}")
async def update_version_controller(
    id: int = Path(...),
    body: dict = Body(...),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:version"])),
) -> JSONResponse:
    version = body.get("version") or ""
    result = await ModelRegistryService.update_version_service(
        auth=auth, id=id, version=version
    )
    return SuccessResponse(data=result, msg="版本更新成功")


@ModelRouter.put("/quota/{id}")
async def update_quota_controller(
    id: int = Path(...),
    body: dict = Body(...),
    auth: AuthSchema = Depends(AuthPermission(["module_model:registry:quota"])),
) -> JSONResponse:
    quota_limit = body.get("quota_limit")
    quota_used = body.get("quota_used")
    result = await ModelRegistryService.update_quota_service(
        auth=auth, id=id, quota_limit=quota_limit, quota_used=quota_used
    )
    return SuccessResponse(data=result, msg="配额更新成功")
