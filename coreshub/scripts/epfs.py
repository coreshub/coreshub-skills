#!/usr/bin/env python3
"""
EPFS 文件系统 CLI

用法：
    python epfs.py list  --zone xb3 --owner <user_id>
    python epfs.py bill  --zone xb3 --owner <user_id> --resource-id <rid>
"""

import json
import sys

import click
import requests

# 兼容两种运行方式：直接 python epfs.py 或 pip install 后调用
try:
    from coreshub.scripts.utils.settings import settings
    from coreshub.scripts.utils.signature import get_signature
    from coreshub.scripts.utils.zones import get_default_zone, list_zones_text
except ImportError:
    from utils.settings import settings
    from utils.signature import get_signature
    from utils.zones import get_default_zone, list_zones_text


def _get(url_path: str, params: dict) -> dict:
    settings.validate()
    signed_query = get_signature(
        method="GET",
        url=url_path,
        ak=settings.access_key,
        sk=settings.secret_key,
        params=params,
    )
    full_url = f"{settings.base_url}{url_path}?{signed_query}"
    resp = requests.get(full_url, timeout=30)
    resp.raise_for_status()
    return resp.json()


@click.group()
def cli():
    """EPFS 弹性并行文件系统管理"""


@cli.command("list")
@click.option("--zone", default=None, help="区域标识（默认从 CORESHUB_ZONES 取第一个）")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--user-id", default=None, envvar="CORESHUB_USER_ID", help="用户 ID")
@click.option("--limit", default=10, show_default=True, help="每页数量")
@click.option("--offset", default=0, show_default=True, help="分页偏移量")
def list_filesystems(zone, owner, user_id, limit, offset):
    """列出已创建的 EPFS 文件系统"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    user_id = user_id or settings.user_id

    try:
        data = _get(
            "/epfs/api/filesystem",
            {"zone": zone, "owner": owner, "user_id": user_id, "limit": limit, "offset": offset},
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"请求失败: HTTP {e.response.status_code}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command("bill")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--user-id", default=None, envvar="CORESHUB_USER_ID", help="用户 ID")
@click.option("--resource-id", required=True, help="资源 ID（从 list 命令获取）")
@click.option("--limit", default=10, show_default=True, help="每页数量")
@click.option("--offset", default=0, show_default=True, help="分页偏移量")
def bill_info(zone, owner, user_id, resource_id, limit, offset):
    """查询 EPFS 文件系统的账单信息"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    user_id = user_id or settings.user_id

    try:
        data = _get(
            "/epfs/api/bill/info",
            {
                "zone": zone,
                "owner": owner,
                "user_id": user_id,
                "resource_id": resource_id,
                "limit": limit,
                "offset": offset,
            },
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"请求失败: HTTP {e.response.status_code}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command("zones")
def show_zones():
    """列出可用区域"""
    print("可用区域：")
    print(list_zones_text())


if __name__ == "__main__":
    cli()
