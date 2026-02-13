# -*- coding: utf-8 -*-

import re
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_

from app.api.v1.module_evaluation.keyword_questionbank.model import KeywordModel
from app.api.v1.module_evaluation.category.model import CategoryModel
from app.api.v1.module_evaluation.keyword_questionbank.schema import (
    KeywordCreateSchema, KeywordUpdateSchema, KeywordOutSchema,
    KeywordMatchRequest, KeywordMatchResult, KeywordMatchResponse
)
from app.api.v1.module_evaluation.keyword_questionbank.crud import KeywordCRUD
from app.core.exceptions import CustomException
from app.utils.excel_util import ExcelUtil


class KeywordService:
    """关键词服务"""

    def __init__(self, crud: KeywordCRUD) -> None:
        self.crud = crud
        self.db = crud.db

    async def _validate_category(self, category_id: int) -> CategoryModel:
        """验证分类"""
        sql = select(CategoryModel).where(CategoryModel.id == category_id)
        category = await self.db.scalar(sql)
        if not category:
            raise CustomException(msg=f"分类ID {category_id} 不存在")
        if not category.status:
            raise CustomException(msg=f"分类 '{category.name}' 未启用")
        return category

    async def _ensure_unique(self, word: str, category_id: int, exclude_id: Optional[int] = None) -> None:
        """确保同分类下关键词唯一"""
        conditions = [
            KeywordModel.word == word,
            KeywordModel.category_id == category_id
        ]
        if exclude_id:
            conditions.append(KeywordModel.id != exclude_id)
        sql = select(KeywordModel).where(and_(*conditions))
        if await self.db.scalar(sql):
            raise CustomException(msg=f"该类别下已存在关键词 '{word}'")

    async def create(self, data: KeywordCreateSchema) -> Dict[str, Any]:
        payload = data.model_dump()
        
        # 验证分类
        await self._validate_category(payload["category_id"])
        
        # 唯一性检查
        await self._ensure_unique(payload["word"], payload["category_id"])

        # JSON字段规范化
        if payload.get("synonyms") is not None:
            payload["synonyms"] = {"items": payload["synonyms"]}
        if payload.get("tags") is not None:
            payload["tags"] = {"items": payload["tags"]}

        obj = await self.crud.create_crud(data=KeywordCreateSchema(**payload))
        return await self._to_out_schema(obj)

    async def update(self, id: int, data: KeywordUpdateSchema) -> Dict[str, Any]:
        obj = await self.crud.get(id=id)
        if not obj:
            raise CustomException(msg="关键词不存在")

        payload = data.model_dump(exclude_unset=True, exclude={"id"})

        # 验证分类
        if "category_id" in payload:
            await self._validate_category(payload["category_id"])

        # 唯一性检查
        if "word" in payload or "category_id" in payload:
            word = payload.get("word", obj.word)
            category_id = payload.get("category_id", obj.category_id)
            await self._ensure_unique(word, category_id, exclude_id=id)

        # JSON字段规范化
        if payload.get("synonyms") is not None:
            payload["synonyms"] = {"items": payload["synonyms"]}
        if payload.get("tags") is not None:
            payload["tags"] = {"items": payload["tags"]}

        new_obj = await self.crud.update_crud(id=id, data=KeywordUpdateSchema(**payload))
        return await self._to_out_schema(new_obj)

    async def delete(self, ids: List[int]) -> None:
        return await self.crud.delete_crud(ids=ids)

    async def list(self, search: Optional[Dict[str, Any]] = None, order_by: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
        rows = await self.crud.get_list_crud(search=search, order_by=order_by)
        return [await self._to_out_schema(r) for r in rows]

    async def get_by_category(self, category_id: int, status: Optional[bool] = None) -> List[Dict[str, Any]]:
        """获取某类别下的关键词"""
        rows = await self.crud.get_by_category(category_id, status)
        return [await self._to_out_schema(r) for r in rows]

    async def _to_out_schema(self, obj: KeywordModel) -> Dict[str, Any]:
        data = KeywordOutSchema.model_validate(obj).model_dump()
        # 解包 JSON 字段
        if data.get("synonyms") and isinstance(data["synonyms"], dict):
            data["synonyms"] = data["synonyms"].get("items", [])
        if data.get("tags") and isinstance(data["tags"], dict):
            data["tags"] = data["tags"].get("items", [])
        # 添加分类名称
        if obj.category:
            data["category_name"] = obj.category.name
        return data

    async def import_items(self, items: List[KeywordCreateSchema]) -> Dict[str, int]:
        """批量导入"""
        created = 0
        skipped = 0
        for item in items:
            try:
                await self.create(item)
                created += 1
            except CustomException:
                skipped += 1
        return {"created": created, "skipped": skipped}

    async def export_list(self, keyword_list: List[Dict[str, Any]]) -> bytes:
        """导出为Excel"""
        if not keyword_list:
            raise CustomException(msg="没有数据可导出")

        mapping_dict = {
            'id': '关键词ID',
            'word': '关键词',
            'category_name': '分类',
            'match_type': '匹配类型',
            'risk_level': '风险等级',
            'weight': '权重',
            'synonyms': '同义词',
            'tags': '标签',
            'status': '状态',
            'hit_count': '命中次数',
            'description': '描述',
            'created_at': '创建时间',
        }

        data = []
        for item in keyword_list:
            row = item.copy()
            row['status'] = '启用' if row.get('status') else '停用'
            # 匹配类型转换
            match_type = row.get('match_type', '').lower()
            if match_type == 'exact':
                row['match_type'] = '精确匹配'
            elif match_type == 'fuzzy':
                row['match_type'] = '模糊匹配'
            elif match_type == 'regex':
                row['match_type'] = '正则匹配'
            # 风险等级转换
            risk_level = row.get('risk_level', '').lower()
            if risk_level == 'high':
                row['risk_level'] = '高'
            elif risk_level == 'medium':
                row['risk_level'] = '中'
            elif risk_level == 'low':
                row['risk_level'] = '低'
            # 列表转字符串
            if isinstance(row.get('synonyms'), list):
                row['synonyms'] = ','.join(row['synonyms'])
            if isinstance(row.get('tags'), list):
                row['tags'] = ','.join(row['tags'])
            data.append(row)

        return ExcelUtil.export_list2excel(list_data=data, mapping_dict=mapping_dict)

    async def match_keywords(self, request: KeywordMatchRequest) -> KeywordMatchResponse:
        """
        关键词匹配算法
        支持精确匹配、模糊匹配、正则匹配
        """
        text = request.text
        matches: List[KeywordMatchResult] = []
        matched_keyword_ids: List[int] = []

        # 获取所有启用的关键词
        keywords = await self.crud.get_all_active()

        # 过滤条件
        if request.category_ids:
            keywords = [k for k in keywords if k.category_id in request.category_ids]
        if request.match_types:
            keywords = [k for k in keywords if k.match_type in request.match_types]

        # 风险等级优先级
        risk_priority = {"high": 3, "medium": 2, "low": 1}
        min_priority = 0
        if request.min_risk_level:
            min_priority = risk_priority.get(request.min_risk_level.lower(), 0)

        for keyword in keywords:
            # 检查最低风险等级
            if risk_priority.get(keyword.risk_level, 0) < min_priority:
                continue

            match_result = self._match_single_keyword(text, keyword)
            if match_result:
                matches.append(match_result)
                matched_keyword_ids.append(keyword.id)

        # 更新命中次数
        if matched_keyword_ids:
            await self.crud.increment_hit_count(matched_keyword_ids)

        # 计算风险评分和最高风险等级
        total_weight = sum(m.weight for m in matches)
        risk_score = min(total_weight / 10.0, 10.0)  # 归一化到0-10

        highest_risk = "low"
        for m in matches:
            if risk_priority.get(m.risk_level, 0) > risk_priority.get(highest_risk, 0):
                highest_risk = m.risk_level

        return KeywordMatchResponse(
            total_matches=len(matches),
            risk_score=round(risk_score, 2),
            highest_risk_level=highest_risk,
            matches=matches
        )

    def _match_single_keyword(self, text: str, keyword: KeywordModel) -> Optional[KeywordMatchResult]:
        """单个关键词匹配"""
        word = keyword.word
        match_type = keyword.match_type
        matched_text = None
        position = None

        if match_type == "exact":
            # 精确匹配
            if word in text:
                position = text.find(word)
                matched_text = word
        elif match_type == "fuzzy":
            # 模糊匹配（忽略大小写）
            lower_text = text.lower()
            lower_word = word.lower()
            if lower_word in lower_text:
                position = lower_text.find(lower_word)
                matched_text = text[position:position + len(word)]
        elif match_type == "regex":
            # 正则匹配
            try:
                pattern = re.compile(word, re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    position = match.start()
                    matched_text = match.group()
            except re.error:
                # 正则表达式无效，跳过
                return None

        # 检查同义词
        if not matched_text and keyword.synonyms:
            synonyms = keyword.synonyms.get("items", []) if isinstance(keyword.synonyms, dict) else []
            for synonym in synonyms:
                if match_type == "exact" and synonym in text:
                    position = text.find(synonym)
                    matched_text = synonym
                    break
                elif match_type == "fuzzy" and synonym.lower() in text.lower():
                    lower_text = text.lower()
                    position = lower_text.find(synonym.lower())
                    matched_text = text[position:position + len(synonym)]
                    break

        if matched_text is None:
            return None

        category_name = keyword.category.name if keyword.category else ""

        return KeywordMatchResult(
            keyword_id=keyword.id,
            word=keyword.word,
            match_type=keyword.match_type,
            risk_level=keyword.risk_level,
            category_id=keyword.category_id,
            category_name=category_name,
            weight=keyword.weight,
            position=position,
            matched_text=matched_text
        )
