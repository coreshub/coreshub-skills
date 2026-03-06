#!/usr/bin/env python3
"""
分布式训练 CLI

用法：
    python training.py list   --zone xb3 --start-at "2025-01-01 00:00:00"
    python training.py logs   --zone xb3 --train-uuid <uuid>
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


def _now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _week_ago_str() -> str:
    return (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")


def _nano_now() -> int:
    return int(datetime.datetime.now().timestamp() * 1_000_000_000)


def _nano_hours_ago(hours: int) -> int:
    return int((datetime.datetime.now() - datetime.timedelta(hours=hours)).timestamp() * 1_000_000_000)


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
    """分布式训练任务管理"""


@cli.command("list")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--start-at", default=None, help="开始时间，格式 'YYYY-MM-DD HH:MM:SS'（默认一周前）")
@click.option("--end-at", default=None, help="结束时间（默认当前时间）")
@click.option("--limit", default=10, show_default=True, help="每页数量")
@click.option("--offset", default=0, show_default=True, help="偏移量")
def list_trainings(zone, owner, start_at, end_at, limit, offset):
    """列出分布式训练任务"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    end_at = end_at or _now_str()
    start_at = start_at or _week_ago_str()
    namespace = settings.user_id.lower()
    url_path = f"/aicp/trains/namespaces/{namespace}/trains"

    try:
        data = _get(
            url_path,
            {"zone": zone, "owner": owner, "end_at": end_at, "start_at": start_at, "limit": limit, "offset": offset},
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
@click.option("--user-id", default=None, envvar="CORESHUB_USER_ID", help="用户 ID")
@click.option("--train-uuid", required=True, help="训练任务 UUID（从 list 命令获取）")
@click.option("--start-time", default=None, type=int, help="开始时间（纳秒时间戳，默认12小时前）")
@click.option("--end-time", default=None, type=int, help="结束时间（纳秒时间戳，默认当前时间）")
@click.option("--size", default=100, show_default=True, help="返回日志条数")
@click.option("--reverse/--no-reverse", default=True, show_default=True, help="是否倒序")
@click.option("--fuzzy/--no-fuzzy", default=True, show_default=True, help="是否模糊匹配")
def training_logs(zone, owner, user_id, train_uuid, start_time, end_time, size, reverse, fuzzy):
    """获取分布式训练任务的详细日志"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    user_id = user_id or settings.user_id
    start_time = start_time or _nano_hours_ago(12)
    end_time = end_time or _nano_now()
    url_path = f"/aicp/trains/namespaces/{user_id.lower()}/endpoints/pytorchjobs/logs"

    try:
        data = _get(
            url_path,
            {
                "zone": zone,
                "owner": owner,
                "user_id": user_id,
                "train_uuid": train_uuid,
                "start_time": start_time,
                "end_time": end_time,
                "size": size,
                "reverse": reverse,
                "fuzzy": fuzzy,
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
