#!/usr/bin/env python3
"""
容器实例（Notebook）CLI

用法：
    python container.py list  --zone xb3
    python container.py ssh   --zone xb3 --uuid <uuid> --namespace <ns>
"""

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
    """容器实例（Notebook）管理"""


@cli.command("list")
@click.option("--zone", default=None, help="区域标识")
@click.option("--limit", default=10, show_default=True, help="返回最大数量")
@click.option("--offset", default=0, show_default=True, help="分页偏移量")
@click.option("--name", default="", help="按实例名称模糊搜索")
def list_containers(zone, limit, offset, name):
    """列出已创建的容器实例"""
    zone = zone or get_default_zone()
    namespace = settings.user_id.lower()
    url_path = f"/aicp/notebooks/namespaces/{namespace}/notebooks"

    try:
        data = _get(url_path, {"zone": zone, "limit": limit, "offset": offset, "name": name})
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"请求失败: HTTP {e.response.status_code}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command("ssh")
@click.option("--zone", default=None, help="区域标识")
@click.option("--uuid", required=True, help="容器实例 UUID（从 list 命令获取）")
@click.option("--namespace", default=None, help="命名空间（默认为账户 ID 小写）")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--user-id", default=None, envvar="CORESHUB_USER_ID", help="用户 ID")
@click.option(
    "--services",
    default="ssh,custom,node_port",
    show_default=True,
    help="要开启的服务，逗号分隔",
)
def ssh_info(zone, uuid, namespace, owner, user_id, services):
    """获取容器实例的 SSH / 端口访问信息"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    user_id = user_id or settings.user_id
    namespace = namespace or settings.user_id.lower()
    services_list = [s.strip() for s in services.split(",") if s.strip()]

    url_path = f"/aicp/notebooks/namespaces/{namespace}/notebooks/{uuid}/servers"
    try:
        data = _get(
            url_path,
            {"zone": zone, "owner": owner, "user_id": user_id, "services": services_list},
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
