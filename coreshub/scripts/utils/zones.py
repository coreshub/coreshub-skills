"""
区域配置工具

通过环境变量 CORESHUB_ZONES 定义区域，格式：
    CORESHUB_ZONES="xb3:西北3区,xb2:西北2区,hb2:华北2区"

未设置时使用内置默认值。
"""

import os
from typing import Dict, List

_DEFAULT_ZONES: Dict[str, str] = {
    "xb3": "西北3区",
    "xb2": "西北2区",
    "hb2": "华北2区",
}


def load_zones() -> Dict[str, str]:
    """从环境变量解析区域配置，失败则使用默认值"""
    raw = os.getenv("CORESHUB_ZONES", "").strip()
    if not raw:
        return dict(_DEFAULT_ZONES)

    zones: Dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            zone_id, _, desc = entry.partition(":")
            zones[zone_id.strip()] = desc.strip()
        else:
            zones[entry] = entry

    return zones if zones else dict(_DEFAULT_ZONES)


# 全局区域字典，模块加载时确定
AVAILABLE_ZONES: Dict[str, str] = load_zones()


def get_zone_ids() -> List[str]:
    """返回所有可用区域 ID 列表"""
    return list(AVAILABLE_ZONES.keys())


def get_default_zone() -> str:
    """返回默认区域（列表第一个）"""
    ids = get_zone_ids()
    return ids[0] if ids else "xb3"


def list_zones_text() -> str:
    """打印可读的区域列表"""
    lines = []
    for zid, desc in AVAILABLE_ZONES.items():
        lines.append(f"  {zid:<6} — {desc}")
    return "\n".join(lines)
