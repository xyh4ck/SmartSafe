# -*- coding: utf-8 -*-

from fastapi import APIRouter

from .testcase.controller import TestCaseRouter
from .dimension.controller import DimensionRouter
from .category.controller import CategoryRouter
from .keyword_questionbank.controller import KeywordQuestionBankRouter
from .testcase_candidate.controller import TestCaseCandidateRouter


EvaluationRouter = APIRouter(prefix="/evaluation")

# 包含所有子路由
EvaluationRouter.include_router(TestCaseRouter)
EvaluationRouter.include_router(DimensionRouter)
EvaluationRouter.include_router(CategoryRouter)
EvaluationRouter.include_router(KeywordQuestionBankRouter)
EvaluationRouter.include_router(TestCaseCandidateRouter)


