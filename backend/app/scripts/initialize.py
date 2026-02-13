# -*- coding: utf-8 -*-

import asyncio
import json
from pathlib import Path
from typing import Dict, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.core.database import AsyncSessionLocal, async_engine
from app.core.base_model import MappedBase
from app.config.setting import settings
from app.api.v1.module_system.user.model import UserModel, UserRolesModel
from app.api.v1.module_system.role.model import RoleModel
from app.api.v1.module_system.dept.model import DeptModel
from app.api.v1.module_system.menu.model import MenuModel
from app.api.v1.module_system.params.model import ParamsModel
from app.api.v1.module_system.dict.model import DictTypeModel, DictDataModel


class InitializeData:
    """
    初始化数据库和基础数据
    """

    def __init__(self) -> None:
        """
        初始化数据库和基础数据
        """
        # 按照依赖关系排序：先创建基础表，再创建关联表
        self.prepare_init_models = [
            # 基础表（项目启动初始化数据表，部门和菜单必须先创建）
            DeptModel,
            MenuModel,
            UserModel,
            RoleModel,
            UserRolesModel,
            ParamsModel,
            DictTypeModel,
            DictDataModel
        ]
    
    async def __init_create_table(self) -> None:
        """
        初始化表结构（第一阶段）
        """
        try:
            # 使用引擎创建所有表
            async with async_engine.begin() as conn:
                await conn.run_sync(MappedBase.metadata.create_all)
            logger.info("✅️ 数据库表结构初始化完成")
        except asyncio.exceptions.TimeoutError:
            logger.error("❌️ 数据库表结构初始化超时")
            raise
        except Exception as e:
            logger.error(f"❌️ 数据库表结构初始化失败: {str(e)}")
            raise

    async def __init_data(self, db: AsyncSession) -> None:
        """
        初始化基础数据

        参数:
        - db (AsyncSession): 异步数据库会话。
        """
        for model in self.prepare_init_models:
            table_name = model.__tablename__
            
            # 检查表中是否已经有数据
            count_result = await db.execute(select(func.count()).select_from(model))
            existing_count = count_result.scalar()
            if existing_count and existing_count > 0:
                logger.warning(f"⚠️  跳过 {table_name} 表数据初始化（表已存在 {existing_count} 条记录）")
                continue

            data = await self.__get_data(table_name)
            if not data:
                logger.warning(f"⚠️  跳过 {table_name} 表，无初始化数据")
                continue
            
            try:
                # 特殊处理具有嵌套 children 数据的表
                if table_name in ["system_dept", "system_menu"]:
                    # 获取对应的模型类
                    model_class = DeptModel if table_name == "system_dept" else MenuModel
                    objs = self.__create_objects_with_children(data, model_class)
                else:
                    # 表为空，直接插入全部数据
                    objs = [model(**item) for item in data]
                db.add_all(objs)
                await db.flush()
                logger.info(f"✅️ 已向 {table_name} 表写入初始化数据")

            except Exception as e:
                logger.error(f"❌️ 初始化 {table_name} 表数据失败: {str(e)}")
                raise

    def __create_objects_with_children(self, data: List[Dict], model_class) -> List:
        """
        通用递归创建对象函数，处理嵌套的 children 数据

        参数:
        - data (List[Dict]): 包含嵌套 children 数据的列表。
        - model_class: 对应的 SQLAlchemy 模型类。

        返回:
        - List: 包含创建的对象的列表。
        """
        objs = []
        
        def create_object(obj_data: Dict):
            # 分离 children 数据
            children_data = obj_data.pop('children', [])
            
            # 创建当前对象
            obj = model_class(**obj_data)
            
            # 递归处理子对象
            if children_data:
                obj.children = [create_object(child) for child in children_data]
                
            return obj
        
        for item in data:
            objs.append(create_object(item))
            
        return objs

    async def __get_data(self, filename: str) -> List[Dict]:
        """
        读取初始化数据文件

        参数:
        - filename (str): 文件名（不包含扩展名）。

        返回:
        - List[Dict]: 解析后的 JSON 数据列表。
        """
        json_path = Path.joinpath(settings.SCRIPT_DIR, f'{filename}.json')
        if not json_path.exists():
            return []

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        except json.JSONDecodeError as e:
            logger.error(f"❌️ 解析 {json_path} 失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌️ 读取 {json_path} 失败: {str(e)}")
            raise

    async def init_db(self) -> None:
        """
        执行完整初始化流程
        """
        # 先创建表结构
        await self.__init_create_table()
        
        # 再初始化数据
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await self.__init_data(session)
                # 确保提交事务
                await session.commit()
    