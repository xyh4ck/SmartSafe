# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.api.v1.module_system.auth.schema import AuthSchema
from app.utils.lang_util import judge_language
from .crud import EvalTaskCRUD, EvalTaskCaseCRUD, EvalTaskResultCRUD, EvalTaskLogCRUD
from .schema import EvalTaskCreateSchema
from ..analyzers.ruleset import default_registry


class EvalTaskService:
    def __init__(self, db: AsyncSession, max_concurrency: int = 5) -> None:
        self.db = db
        self.auth = AuthSchema(db=db)
        self.task_crud = EvalTaskCRUD(self.auth)
        self.case_crud = EvalTaskCaseCRUD(self.auth)
        self.result_crud = EvalTaskResultCRUD(self.auth)
        self.log_crud = EvalTaskLogCRUD(self.auth)
        self.registry = default_registry()
        self.sem = asyncio.Semaphore(max_concurrency)  # 限制LLM并发调用数

    def _get_translation_system_message(self) -> str:
        """获取翻译的 system 消息"""
        return """You are a professional Chinese native translator who needs to fluently translate text into Chinese.

## Translation Rules
1. Output only the translated content, without explanations or additional content (such as "Here's the translation:" or "Translation as follows:")
2. The returned translation must maintain exactly the same number of paragraphs and format as the original text
3. If the text contains HTML tags, consider where the tags should be placed in the translation while maintaining fluency
4. For content that should not be translated (such as proper nouns, code, etc.), keep the original text.

## OUTPUT FORMAT:
- **Single paragraph input** → Output translation directly (no separators, no extra text)"""

    def _get_translation_user_prompt(self, text: str) -> str:
        """获取翻译的 user 提示"""
        return f"Translate to Chinese (output translation only):\n\n{text}"

    async def _a_translate_reason(self, reason: str, llm_provider: str, llm_params: dict) -> str:
        """翻译 reason 文本（异步版本）"""
        if not isinstance(reason, str) or not reason.strip():
            return reason
        
        # 使用 judge_language 判断是否需要翻译
        lang = judge_language(reason)
        if lang == "chinese":
            return reason
        
        # 非中文内容需要翻译
        system_message = self._get_translation_system_message()
        user_prompt = self._get_translation_user_prompt(reason)
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            async with self.sem:
                result = await self._generate_output_with_messages(
                    messages, llm_provider, llm_params
                )
            translated = (result.get("content") or "").strip()
            return translated if translated else reason
        except Exception as e:
            logger.warning(f"翻译失败，保留原文: {e}")
            return reason

    async def create_task(self, data: EvalTaskCreateSchema) -> int:
        task = await self.task_crud.create_task(
            {
                "name": data.name,
                "status": "queued",
                "total_cases": len(data.cases),
                "finished_cases": 0,
                "risk_summary": None,
                "started_at": None,
                "finished_at": None,
            }
        )
        # 记录日志
        await self.log_crud.write_log(
            task_id=task.id,
            stage="create",
            message=f"创建任务: {data.name}",
            level="INFO",
        )

        # 创建用例
        for c in data.cases:
            await self.case_crud.create_case(
                {
                    "task_id": task.id,
                    "prompt": c.prompt,
                    "llm_provider": c.llm_provider,
                    "llm_params": json.dumps(c.llm_params or {}, ensure_ascii=False),
                    "status": "queued",
                }
            )

        return task.id

    async def run_task(self, task_id: int) -> None:
        """执行评测任务 - 重构版本，使用独立session处理每个用例"""
        from app.core.database import AsyncSessionLocal
        
        # 更新任务状态为运行中
        task = await self.task_crud.get_by_id(task_id)
        if not task:
            logger.error(f"任务 {task_id} 不存在")
            return
            
        await self.task_crud.update_task(
            task.id, {"status": "running", "started_at": datetime.now()}
        )
        await self.log_crud.write_log(
            task_id=task.id, stage="start", message="任务开始执行"
        )
        await self.db.commit()
        logger.info(f"任务 {task_id} 开始执行")

        # 查询所有用例
        cases = await self.case_crud.list_cases(search={"task_id": task.id})
        logger.info(f"任务 {task_id} 共有 {len(cases)} 个用例")
        
        if not cases:
            logger.warning(f"任务 {task_id} 没有用例")
            return
        
        results: List[Dict[str, Any]] = []
        completed_count = 0  # 用于跟踪完成的用例数
        count_lock = asyncio.Lock()  # 保护计数器

        async def process_single_case(case_id: int, prompt: str, llm_provider: str, llm_params: dict) -> None:
            """处理单个用例 - 使用完全独立的session"""
            nonlocal completed_count, results  # 声明使用外层变量
            logger.info(f"开始处理用例 {case_id}")
            
            try:
                # 步骤1: 更新用例状态为running
                async with AsyncSessionLocal() as db:
                    async with db.begin():
                        auth = AuthSchema(db=db)
                        case_crud = EvalTaskCaseCRUD(auth)
                        log_crud = EvalTaskLogCRUD(auth)
                        
                        await case_crud.update_case(
                            case_id, {"status": "running", "started_at": datetime.now()}
                        )
                        await log_crud.write_log(
                            task_id=task_id,
                            case_id=case_id,
                            stage="generate",
                            message="开始生成输出",
                        )
                logger.info(f"用例 {case_id} 状态已更新为 running")
                
                # 步骤2: 调用LLM（受信号量限制，最多5个并发）
                async with self.sem:
                    logger.info(f"用例 {case_id} 开始调用LLM")
                    llm_result = await self._generate_output(prompt, llm_provider, llm_params)
                    
                output_text = llm_result.get("content", "")
                token_usage = llm_result.get("usage", {})
                logger.info(f"用例 {case_id} LLM调用完成，输出长度: {len(output_text)}")
                
                # 步骤3: 分析输出
                analysis = self.registry.analyze_all(prompt, output_text)
                scores = analysis.get("keywords", {}).get("scores", {})

                deepteam = analysis.get("deepteam_eval", {})
                deepteam_score = deepteam.get("score")
                if deepteam_score is not None:
                    try:
                        scores["deepteam_eval"] = int(deepteam_score)
                    except Exception:
                        pass

                deepteam_details = deepteam.get("details") or {}
                if isinstance(deepteam_details, dict):
                    for vuln_name, info in deepteam_details.items():
                        if not isinstance(vuln_name, str):
                            continue
                        if not isinstance(info, dict):
                            continue
                        if "score" not in info:
                            continue
                        s = info.get("score")
                        if s is None:
                            continue
                        try:
                            # 仅允许 0/1 分数落库
                            normalized = 0 if float(s) > 0 else 1
                            scores[f"deepteam:{vuln_name}"] = int(normalized)
                        except Exception:
                            continue

                risk_reason = str(deepteam.get("reason") or "")
                if risk_reason:
                    risk_reason = await self._a_translate_reason(risk_reason, llm_provider, llm_params)

                scores_for_risk_level = dict(scores)
                dt_eval = scores_for_risk_level.get("deepteam_eval")
                if dt_eval in (0, 1):
                    scores_for_risk_level["deepteam_eval"] = 1 - int(dt_eval)

                risk_level = self.registry.risk_level(scores_for_risk_level)
                logger.info(f"用例 {case_id} 风险分析完成，风险等级: {risk_level}")
                
                # 步骤4: 更新用例结果和进度
                async with AsyncSessionLocal() as db:
                    async with db.begin():
                        auth = AuthSchema(db=db)
                        case_crud = EvalTaskCaseCRUD(auth)
                        log_crud = EvalTaskLogCRUD(auth)
                        task_crud = EvalTaskCRUD(auth)
                        
                        # 更新用例结果
                        await case_crud.update_case(case_id, {
                            "status": "succeeded",
                            "output_text": output_text,
                            "risk_scores": json.dumps(scores, ensure_ascii=False),
                            "risk_level": risk_level,
                            "risk_reason": risk_reason,
                            "completion_tokens": token_usage.get("completion_tokens"),
                            "prompt_tokens": token_usage.get("prompt_tokens"),
                            "total_tokens": token_usage.get("total_tokens"),
                            "finished_at": datetime.now(),
                        })
                        
                        # 写日志
                        await log_crud.write_log(
                            task_id=task_id,
                            case_id=case_id,
                            stage="complete",
                            message="用例处理成功",
                        )
                        
                logger.info(f"用例 {case_id} 处理成功")
                
                # 更新内存计数器（避免数据库死锁）
                async with count_lock:
                    completed_count += 1
                    results.append({"case_id": case_id, "scores": scores, "risk_level": risk_level})
                
            except Exception as e:
                logger.error(f"用例 {case_id} 处理失败: {str(e)}", exc_info=True)
                try:
                    # 更新失败状态
                    async with AsyncSessionLocal() as db:
                        async with db.begin():
                            auth = AuthSchema(db=db)
                            case_crud = EvalTaskCaseCRUD(auth)
                            log_crud = EvalTaskLogCRUD(auth)
                            
                            await case_crud.update_case(case_id, {
                                "status": "failed",
                                "error": str(e)[:500],  # 限制错误信息长度
                                "finished_at": datetime.now(),
                            })
                            
                            await log_crud.write_log(
                                task_id=task_id,
                                case_id=case_id,
                                stage="error",
                                message=f"处理失败: {str(e)[:200]}",
                                level="ERROR",
                            )
                    
                    # 更新内存计数器
                    async with count_lock:
                        completed_count += 1
                        
                except Exception as inner_e:
                    logger.error(f"用例 {case_id} 错误处理失败: {str(inner_e)}", exc_info=True)
                    # 即使错误处理失败，也要更新计数器
                    async with count_lock:
                        completed_count += 1

        # 并发处理所有用例
        logger.info(f"开始并发处理 {len(cases)} 个用例")
        tasks = [
            process_single_case(
                c.id,
                c.prompt,
                c.llm_provider,
                json.loads(c.llm_params) if c.llm_params else {}
            )
            for c in cases
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"所有用例处理完成，成功: {len(results)}/{len(cases)}, 完成数: {completed_count}")
        
        # 使用新的独立会话更新任务状态（避免长时间操作后连接超时）
        async with AsyncSessionLocal() as db:
            async with db.begin():
                auth = AuthSchema(db=db)
                task_crud = EvalTaskCRUD(auth)
                result_crud = EvalTaskResultCRUD(auth)
                log_crud = EvalTaskLogCRUD(auth)
                
                # 一次性更新完成的用例数
                await task_crud.update_task(task.id, {"finished_cases": completed_count})
                logger.info(f"任务 {task_id} 进度已更新: {completed_count}/{len(cases)}")

                # 汇总结果
                summary, metrics, top_risks = self._summarize(
                    results, total_cases=len(cases), finished_cases=completed_count
                )
                await result_crud.upsert_result(
                    task_id=task.id, 
                    summary=json.dumps(summary, ensure_ascii=False), 
                    metrics=json.dumps(metrics, ensure_ascii=False), 
                    top_risks=json.dumps(top_risks, ensure_ascii=False)
                )
                succeeded_cases = len(results)
                failed_cases = max(int(completed_count) - int(succeeded_cases), 0)
                if failed_cases == 0:
                    final_status = "completed"
                elif succeeded_cases == 0:
                    final_status = "failed"
                else:
                    final_status = "partial"
                await task_crud.update_task(
                    task.id, {"status": final_status, "finished_at": datetime.now()}
                )
                await log_crud.write_log(
                    task_id=task.id,
                    stage="complete",
                    message=f"任务执行完成，最终状态: {final_status}，成功: {succeeded_cases}，失败: {failed_cases}",
                )
        logger.info(f"任务 {task_id} 执行完成")

    async def _generate_output(
        self, prompt: str, llm_provider: str, llm_params: dict
    ) -> dict:
        """调用LLM生成输出，返回包含content和usage的字典"""
        try:
            # 导入所需模块
            from app.api.v1.module_model.llm_model.service import ModelRegistryService
            from app.api.v1.module_model.llm_model.crud import ModelRegistryCRUD
            from app.utils.hash_bcrpy_util import AESCipher
            import hashlib
            from app.core.database import AsyncSessionLocal

            model_name = llm_params.get("model", "")

            async with AsyncSessionLocal() as db:
                auth = AuthSchema(db=db)
                model_crud = ModelRegistryCRUD(auth)
                model_obj = await model_crud.get(name=model_name)

            api_key = None
            if model_obj:
                logger.info(
                    f"找到模型配置: {model_name}, api_key_enc: {model_obj.api_key_enc}"
                )
                if model_obj.api_key_enc:
                    # 解密 API key
                    key = hashlib.sha256(b"/model_registry").digest()
                    try:
                        encrypted_data = model_obj.api_key_enc
                        api_key = AESCipher(key).decrypt(encrypted_data)
                        logger.info(
                            f"API key解密成功，长度: {len(api_key) if api_key else 0}"
                        )
                    except Exception as e:
                        logger.error(f"解密API key失败: {str(e)}", exc_info=True)
                        api_key = None
            else:
                logger.warning(f"未找到模型配置: {model_name}")

            # 调用LLM生成内容
            result = await ModelRegistryService.generate_service(
                auth=self.auth,
                provider=llm_provider,
                model=model_name,
                api_base=llm_params.get("api_base"),
                api_key=api_key,
                prompt=prompt,
            )
            logger.info(f"LLM调用成功: content长度={len(result.get('content', ''))}, usage={result.get('usage')}")
            return result
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            # 如果调用失败，返回错误信息
            return {
                "content": f"[LLM调用失败: {str(e)}]",
                "usage": {}
            }

    async def _generate_output_with_messages(
        self, messages: List[Dict[str, str]], llm_provider: str, llm_params: dict
    ) -> dict:
        """调用LLM生成输出（使用messages结构），返回包含content和usage的字典"""
        try:
            from app.api.v1.module_model.llm_model.service import ModelRegistryService
            from app.api.v1.module_model.llm_model.crud import ModelRegistryCRUD
            from app.utils.hash_bcrpy_util import AESCipher
            import hashlib
            from app.core.database import AsyncSessionLocal

            model_name = llm_params.get("model", "")

            async with AsyncSessionLocal() as db:
                auth = AuthSchema(db=db)
                model_crud = ModelRegistryCRUD(auth)
                model_obj = await model_crud.get(name=model_name)

            api_key = None
            if model_obj and model_obj.api_key_enc:
                key = hashlib.sha256(b"/model_registry").digest()
                try:
                    api_key = AESCipher(key).decrypt(model_obj.api_key_enc)
                except Exception as e:
                    logger.error(f"解密API key失败: {str(e)}")
                    api_key = None

            result = await ModelRegistryService.generate_service(
                auth=self.auth,
                provider=llm_provider,
                model=model_name,
                api_base=llm_params.get("api_base"),
                api_key=api_key,
                prompt="",
                messages=messages,
            )
            return result
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            return {"content": "", "usage": {}}

    def _summarize(
        self, results: List[Dict[str, Any]], total_cases: int, finished_cases: int
    ) -> tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        count = len(results) or 1
        dim_totals: Dict[str, float] = {}
        level_counts: Dict[str, int] = {}
        for r in results:
            scores: Dict[str, float] = r.get("scores", {})
            for k, v in scores.items():
                dim_totals[k] = dim_totals.get(k, 0.0) + float(v)
            lvl = r.get("risk_level") or "Low"
            level_counts[lvl] = level_counts.get(lvl, 0) + 1

        metrics = {k: round(v / count, 4) for k, v in dim_totals.items()}
        succeeded_cases = len(results)
        failed_cases = max(int(finished_cases) - int(succeeded_cases), 0)
        qualified_cases = sum(1 for r in results if (r.get("risk_level") or "Low") == "Low")
        qualified_rate = round((qualified_cases / total_cases) * 100, 2) if total_cases else 0.0
        summary = {
            "level_distribution": level_counts,
            "total_cases": int(total_cases),
            "finished_cases": int(finished_cases),
            "succeeded_cases": int(succeeded_cases),
            "failed_cases": int(failed_cases),
            "qualified_cases": int(qualified_cases),
            "qualified_rate": qualified_rate,
        }
        top_risks = sorted(
            results, key=lambda x: sum((x.get("scores") or {}).values()), reverse=True
        )[:10]
        return summary, metrics, top_risks
