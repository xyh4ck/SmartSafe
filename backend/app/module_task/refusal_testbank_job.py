# -*- coding: utf-8 -*-

"""
拒答测试题库月度更新任务

功能：
1. 每月自动检查题库覆盖度
2. 根据缺口自动生成候选题
3. 生成的候选题需人工审核后发布

配置方式：
在系统任务管理中添加定时任务，配置如下：
- 调用目标：refusal_testbank_job.monthly_generate_candidates
- 触发器类型：cron
- Cron表达式：0 0 9 1 * ? *  （每月1日9点执行）
"""

from datetime import datetime
from app.core.database import AsyncSessionLocal
from app.core.logger import logger


async def monthly_generate_candidates(
    refusal_expectation: str = "should_refuse",
    count_per_category: int = 5,
):
    """
    月度自动生成候选题任务入口
    
    参数:
    - refusal_expectation: 拒答期望类型，should_refuse 或 should_not_refuse
    - count_per_category: 每个分类生成的题目数量
    """
    from app.api.v1.module_evaluation.testcase_candidate.model import TestCaseCandidateModel
    from app.api.v1.module_evaluation.testcase_candidate.crud import TestCaseCandidateCRUD
    from app.api.v1.module_evaluation.testcase_candidate.service import TestCaseCandidateService
    from app.core.base_crud import AuthSchema
    
    logger.info(f"[月度任务] 开始执行拒答题库更新任务: refusal_expectation={refusal_expectation}")
    
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                auth = AuthSchema(db=session)
                crud = TestCaseCandidateCRUD(model=TestCaseCandidateModel, auth=auth)
                service = TestCaseCandidateService(crud)
                
                # 获取覆盖度统计
                coverage = await service.get_coverage()
                
                # 记录当前覆盖度
                if refusal_expectation == "should_refuse":
                    total = coverage["should_refuse"]["total"]
                    gaps = coverage["should_refuse"]["gaps"]
                    logger.info(f"[月度任务] 应拒答题库: 总量={total}, 缺口分类数={len(gaps)}")
                else:
                    total = coverage["should_not_refuse"]["total"]
                    gaps = coverage["should_not_refuse"]["gaps"]
                    logger.info(f"[月度任务] 非拒答题库: 总量={total}, 缺口方面数={len(gaps)}")
                
                # 如果有缺口，自动生成候选题
                if gaps:
                    result = await service.generate_candidates(
                        refusal_expectation=refusal_expectation,
                        category_ids=None,  # 自动根据缺口选择
                        count_per_category=count_per_category,
                    )
                    logger.info(f"[月度任务] 生成完成: batch_id={result.get('batch_id')}, generated={result.get('generated')}")
                else:
                    logger.info(f"[月度任务] 无缺口，跳过生成")
                
    except Exception as e:
        logger.error(f"[月度任务] 执行失败: {str(e)}")
        raise


async def monthly_generate_all():
    """
    月度生成所有类型的候选题（应拒答 + 非拒答）
    """
    logger.info("[月度任务] 开始执行全量拒答题库更新任务")
    
    # 生成应拒答候选题
    await monthly_generate_candidates(
        refusal_expectation="should_refuse",
        count_per_category=5,
    )
    
    # 生成非拒答候选题
    await monthly_generate_candidates(
        refusal_expectation="should_not_refuse",
        count_per_category=5,
    )
    
    logger.info("[月度任务] 全量拒答题库更新任务执行完成")
