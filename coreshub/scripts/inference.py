#!/usr/bin/env python3
"""
推理服务 CLI

用法：
    python inference.py list  --zone xb3 --owner <user_id>
    python inference.py logs  --zone xb3 --service-id <sid>
"""

import datetime
import json
import sys

import click
import requests

try:
    from coreshub.scripts.utils.settings import settings
    from coreshub.scripts.utils.signature import get_signature
    from coreshub.scripts.utils.zones import get_default_zone, list_zones_text
except ImportError:
    from utils.settings import settings
    from utils.signature import get_signature
    from utils.zones import get_default_zone, list_zones_text


def _utc_now_str() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _utc_hours_ago_str(hours: int) -> str:
    t = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


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
    """推理服务管理"""


@cli.command("list")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--key-words", default="", help="按服务名称关键字搜索")
@click.option("--page", default=1, show_default=True, help="页码")
@click.option("--size", default=10, show_default=True, help="每页数量")
def list_services(zone, owner, key_words, page, size):
    """列出已创建的推理服务"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id

    try:
        data = _get(
            "/maas/api/inference_service",
            {"zone": zone, "owner": owner, "key_words": key_words, "page": page, "size": size},
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"请求失败: HTTP {e.response.status_code}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command("logs")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--service-id", required=True, help="推理服务 ID（从 list 命令获取）")
@click.option("--start-time", default=None, help="开始 UTC 时间，格式 'YYYY-MM-DDTHH:MM:SS.000Z'（默认24小时前）")
@click.option("--end-time", default=None, help="结束 UTC 时间（默认当前时间）")
@click.option("--size", default=100, show_default=True, help="返回日志条数")
@click.option("--reverse/--no-reverse", default=True, show_default=True, help="是否倒序")
def service_logs(zone, owner, service_id, start_time, end_time, size, reverse):
    """获取推理服务日志"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    end_time = end_time or _utc_now_str()
    start_time = start_time or _utc_hours_ago_str(24)
    url_path = f"/maas/api/inference_service/{service_id}/log"

    params = {
        "zone": zone,
        "owner": owner,
        "service_id": service_id,
        "size": size,
        "reverse": reverse,
        "start_time": start_time,
        "end_time": end_time,
    }

    try:
        data = _get(url_path, params)
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
