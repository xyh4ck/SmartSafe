# -*- coding: utf-8 -*-
"""
集中式路由发现与注册

约定：
- 仅扫描 `app.api.v1` 包内，顶级目录以 `module_` 开头的模块。
- 在各模块任意子目录下的 `controller.py` 中定义的 `APIRouter` 实例会自动被注册。
- 顶级目录 `module_xxx` 会映射为容器路由前缀 `/<xxx>`。

设计目标：
- 稳定、可预测：有序扫描与注册，确定性日志输出。
- 简洁、易维护：职责拆分成小函数，类型提示与清晰注释。
- 安全、可控：去重处理、异常分层记录、可配置的前缀映射与忽略规则。
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple, List

from fastapi import APIRouter

from app.core.logger import logger

# ----- 约定与配置 -----
MODULE_PREFIX = "module_"

# 可选：前缀映射与忽略规则（需要时可在此处进行配置）
PREFIX_MAP: Dict[str, str] = {
    # e.g. "module_application": "/application",
}
EXCLUDE_DIRS: Set[str] = set()
EXCLUDE_FILES: Set[str] = set()

# 创建根路由（对外暴露）
router = APIRouter()

# 记录已注册的 APIRouter，避免重复 include（既包含控制器路由，也包含容器路由）
_seen_router_ids: Set[int] = set()


# ----- 工具函数 -----
def _get_v1_base_dir_and_pkg() -> Tuple[Path, str]:
    """定位 `app.api.v1` 包的文件系统路径与包名。

    返回:
    - (Path, str): (`app/api/v1` 的路径, 包名 `app.api.v1`)
    """
    try:
        v1_pkg = importlib.import_module("app.api.v1")
        base_dir = Path(next(iter(v1_pkg.__path__)))
        base_pkg = v1_pkg.__name__
        return base_dir, base_pkg
    except Exception as e:
        logger.error(f"❌️ 定位 app.api.v1 失败: {e}")
        raise


def _iter_controller_files(base_dir: Path) -> Iterable[Path]:
    """递归查找并返回所有 `controller.py` 文件，按路径排序保证确定性。"""
    return sorted(base_dir.rglob("controller.py"), key=lambda p: p.as_posix())


def _resolve_prefix(top_module: str) -> Optional[str]:
    """将顶级模块目录名解析为容器前缀。

    - 过滤被忽略的目录。
    - 仅处理以 `module_` 开头的目录。
    - 支持通过 `PREFIX_MAP` 自定义映射，否则默认 `/<xxx>`。
    """
    if top_module in EXCLUDE_DIRS:
        return None
    if not top_module.startswith(MODULE_PREFIX):
        return None
    mapped = PREFIX_MAP.get(top_module)
    return mapped or f"/{top_module[len(MODULE_PREFIX):]}"


def _include_module_routers(mod: object, container: APIRouter) -> int:
    """将模块中的所有 `APIRouter` 实例包含到指定容器路由中。

    返回:
    - int: 新增注册的路由数量
    """
    from fastapi import APIRouter as _APIRouter

    added = 0
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name, None)
        if isinstance(attr, _APIRouter):
            rid = id(attr)
            if rid in _seen_router_ids:
                continue
            _seen_router_ids.add(rid)
            container.include_router(attr)
            added += 1
    return added


# ----- 主流程 -----
def _discover_and_register() -> None:
    """通过文件系统递归扫描并注册路由到根路由。"""
    base_dir, base_pkg = _get_v1_base_dir_and_pkg()
    containers: Dict[str, APIRouter] = {}
    container_counts: Dict[str, int] = {}

    scanned_files = 0
    imported_modules = 0
    included_routers = 0

    for file in _iter_controller_files(base_dir):
        rel_path = file.relative_to(base_dir).as_posix()
        scanned_files += 1

        if rel_path in EXCLUDE_FILES:
            continue

        parts = file.relative_to(base_dir).parts
        if len(parts) < 2:
            # 至少应包含顶级目录和文件名（如 module_xxx/.../controller.py）
            continue

        top_module = parts[0]
        prefix = _resolve_prefix(top_module)
        if not prefix:
            # 非约定模块或被忽略
            continue

        # 拼接模块导入路径: app.api.v1.<...>.controller
        mod_path = ".".join((base_pkg,) + tuple(parts[:-1]) + ("controller",))
        try:
            mod = importlib.import_module(mod_path)
            imported_modules += 1
        except ModuleNotFoundError:
            logger.warning(f"❌️ 未找到控制器模块: {mod_path}")
            continue
        except Exception as e:
            logger.error(f"❌️ 导入控制器失败: {mod_path} -> {e}")
            continue

        container = containers.setdefault(prefix, APIRouter(prefix=prefix))
        try:
            added = _include_module_routers(mod, container)
            included_routers += added
            container_counts[prefix] = container_counts.get(prefix, 0) + added
        except Exception as e:
            logger.error(f"❌️ 注册控制器路由失败: {mod_path} -> {e}")

    # 将容器路由按前缀名称排序后注册到根路由，保证顺序稳定
    for prefix in sorted(containers.keys()):
        container = containers[prefix]
        rid = id(container)
        if rid in _seen_router_ids:
            continue
        _seen_router_ids.add(rid)
        router.include_router(container)
        # 更丰富的注册日志（含路由数量）
        logger.info(f"✅️ 已注册模块容器: {prefix}")

    logger.info(
        (
            f"✅️ 路由发现完成: 扫描文件 {scanned_files}, "
            f"导入模块 {imported_modules}, 注册路由 {included_routers}, "
            f"容器 {len(containers)}"
        )
    )


# 执行自动发现注册（模块导入即生效）
_discover_and_register()