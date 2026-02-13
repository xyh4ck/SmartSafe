# -*- coding: utf-8 -*-

from fastapi import APIRouter

def get_router() -> APIRouter:
    router = APIRouter(prefix="/evaltask")
    from .evaltask.controller import EvalTaskRouter
    router.include_router(EvalTaskRouter)
    return router
