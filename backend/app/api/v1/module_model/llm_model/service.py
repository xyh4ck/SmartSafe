from typing import Dict, List, Optional
import hashlib
import asyncio
from functools import partial
from litellm import completion

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.exceptions import CustomException
from app.utils.hash_bcrpy_util import AESCipher
from .crud import ModelRegistryCRUD
from .schema import (
    ModelRegistryCreateSchema,
    ModelRegistryUpdateSchema,
    ModelRegistryOutSchema,
)


class ModelRegistryService:
    @staticmethod
    async def detail_service(auth: AuthSchema, id: int) -> Dict:
        obj = await ModelRegistryCRUD(auth).get_by_id_crud(id=id)
        if not obj:
            raise CustomException(msg="数据不存在")
        return ModelRegistryOutSchema.model_validate(obj).model_dump()

    @staticmethod
    async def list_service(
        auth: AuthSchema,
        search: Optional[Dict] = None,
        order_by: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict]:
        objs = await ModelRegistryCRUD(auth).get_list_crud(
            search=search, order_by=order_by
        )
        return [ModelRegistryOutSchema.model_validate(o).model_dump() for o in objs]

    @staticmethod
    async def create_service(auth: AuthSchema, data: ModelRegistryCreateSchema) -> Dict:
        exists = await ModelRegistryCRUD(auth).get(name=data.name)
        if exists:
            raise CustomException(msg="名称已存在")
        api_key_enc = None
        if data.api_key:
            key = hashlib.sha256(b"/model_registry").digest()
            api_key_enc = AESCipher(key).encrypt(data.api_key).hex()
        obj = await ModelRegistryCRUD(auth).create(
            {
                "name": data.name,
                "provider": data.provider,
                "type": data.type,
                "api_base": data.api_base,
                "api_key_enc": api_key_enc,
                "available": data.available if data.available is not None else True,
                "version": data.version,
                "quota_limit": data.quota_limit or 0,
                "description": data.description,
            }
        )
        return ModelRegistryOutSchema.model_validate(obj).model_dump()

    @staticmethod
    async def update_service(
        auth: AuthSchema, id: int, data: ModelRegistryUpdateSchema
    ) -> Dict:
        obj = await ModelRegistryCRUD(auth).get_by_id_crud(id=id)
        if not obj:
            raise CustomException(msg="数据不存在")
        payload = data.model_dump(exclude_unset=True)
        if "name" in payload and payload["name"] != obj.name:
            dup = await ModelRegistryCRUD(auth).get(name=payload["name"])
            if dup:
                raise CustomException(msg="名称已存在")
        if payload.get("api_key"):
            key = hashlib.sha256(b"/model_registry").digest()
            payload["api_key_enc"] = (
                AESCipher(key).encrypt(payload.pop("api_key")).hex()
            )
        updated = await ModelRegistryCRUD(auth).update(id=id, data=payload)
        return ModelRegistryOutSchema.model_validate(updated).model_dump()

    @staticmethod
    async def delete_service(auth: AuthSchema, ids: List[int]) -> None:
        await ModelRegistryCRUD(auth).delete(ids=ids)

    @staticmethod
    async def connectivity_test_service(auth: AuthSchema, id: int) -> Dict:
        obj = await ModelRegistryCRUD(auth).get_by_id_crud(id=id)
        if not obj:
            raise CustomException(msg="数据不存在")
        api_key = None
        if obj.api_key_enc:
            key = hashlib.sha256(b"/model_registry").digest()
            try:
                api_key = AESCipher(key).decrypt(obj.api_key_enc)
            except Exception:
                api_key = None
        try:
            resp = (
                completion(
                    model=obj.name,
                    messages=[{"role": "user", "content": "Hello."}],
                    api_base=obj.api_base,
                    api_key=api_key,
                )
                .choices[0]
                .message
            )
            return {"success": True, "status": 200, "msg": resp}
        except Exception as e:
            return {"success": False, "status": 0, "msg": str(e)}

    @staticmethod
    async def batch_available_service(
        auth: AuthSchema, ids: List[int], status: bool
    ) -> None:
        await ModelRegistryCRUD(auth).set(ids=ids, available=status)

    @staticmethod
    async def update_version_service(auth: AuthSchema, id: int, version: str) -> Dict:
        updated = await ModelRegistryCRUD(auth).update(id=id, data={"version": version})
        return ModelRegistryOutSchema.model_validate(updated).model_dump()

    @staticmethod
    async def update_quota_service(
        auth: AuthSchema,
        id: int,
        quota_limit: Optional[int] = None,
        quota_used: Optional[int] = None,
    ) -> Dict:
        data = {}
        if quota_limit is not None:
            data["quota_limit"] = quota_limit
        if quota_used is not None:
            data["quota_used"] = quota_used
        updated = await ModelRegistryCRUD(auth).update(id=id, data=data)
        return ModelRegistryOutSchema.model_validate(updated).model_dump()

    @staticmethod
    async def generate_service(
        auth: AuthSchema,
        provider: str,
        model: str,
        api_base: Optional[str],
        api_key: Optional[str],
        prompt: str,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        """调用LLM生成内容，返回内容和token使用情况
        
        Args:
            messages: 可选，完整的消息列表（优先于prompt）
            prompt: 单条用户消息（当messages为空时使用）
        """
        from app.core.logger import logger

        try:
            logger.info(
                f"调用LLM - provider: {provider}, model: {model}, api_base: {api_base}, has_api_key: {bool(api_key)}"
            )
            # 优先使用 messages 参数，否则使用 prompt 构建单条消息
            if messages:
                final_messages = messages
            else:
                final_messages = [{"role": "user", "content": prompt}]
            
            loop = asyncio.get_running_loop()
            call = partial(
                completion,
                model=model,
                messages=final_messages,
                api_base=api_base,
                api_key=api_key,
            )
            response = await loop.run_in_executor(None, call)
            content = response.choices[0].message.content or ""
            
            # 如果content是字节串，解码为UTF-8
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            # 提取token使用情况
            usage = response.usage
            token_usage = {
                "completion_tokens": usage.completion_tokens if usage else None,
                "prompt_tokens": usage.prompt_tokens if usage else None,
                "total_tokens": usage.total_tokens if usage else None,
            }
            
            # 记录返回内容的前100个字符用于调试
            logger.info(f"LLM返回内容（前100字符）: {content[:100]}")
            logger.info(f"Token使用情况: {token_usage}")
            
            return {
                "content": content,
                "usage": token_usage
            }
        except Exception as e:
            logger.error(f"LLM调用失败 - model: {model}, error: {str(e)}")
            raise CustomException(msg=f"LLM调用失败: {str(e)}")
