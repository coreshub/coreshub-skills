#!/usr/bin/env python3
"""
iMaaS 大模型服务 CLI

用法：
    python imaas.py models   --zone xb3 --owner <user_id>
    python imaas.py model    --zone xb3 --model-id md-xxx
    python imaas.py apikeys  --zone xb3 --owner <user_id>
    python imaas.py metrics  --zone xb3 --start-time <unix_ts>
"""

import json
import sys
import time as _time

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

_DEFAULT_MODEL_TAGS = "txt2txt,txt2img,txt2video,img2video,audio,embedding,rerank,crossmodel"


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
    """iMaaS 大模型服务管理"""


@cli.command("models")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--key-words", default="", help="按模型名称关键字模糊搜索")
@click.option(
    "--model-tag",
    default=_DEFAULT_MODEL_TAGS,
    show_default=True,
    help=(
        "按模型类型筛选，逗号分隔。"
        "可选：txt2txt,txt2img,txt2video,img2video,audio,embedding,rerank,crossmodel"
    ),
)
@click.option("--page", default=1, show_default=True, help="页码，从 1 开始")
@click.option("--size", default=100, show_default=True, help="每页返回数量")
def list_models(zone, owner, key_words, model_tag, page, size):
    """查看 iMaaS 大模型服务广场上可调用的模型列表"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id

    try:
        data = _get(
            "/imaas/api/model",
            {
                "zone": zone,
                "owner": owner,
                "key_words": key_words,
                "model_tag": model_tag,
                "page": page,
                "size": size,
            },
        )
        # 过滤 icon 字段（base64 图片，占用大量空间）
        for item in data.get("list", []):
            item.pop("icon", None)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"请求失败: HTTP {e.response.status_code}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command("model")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--model-id", required=True, help="模型 ID，如 md-tDz8i3XJ（从 models 命令获取）")
def model_detail(zone, owner, model_id):
    """获取单个 iMaaS 模型的详细信息（包含价格、参数、渠道配置等）"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    url_path = f"/imaas/api/model/{model_id}"

    try:
        data = _get(url_path, {"zone": zone, "owner": owner})
        # 过滤 icon 字段
        if isinstance(data.get("data"), dict):
            data["data"].pop("icon", None)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"请求失败: HTTP {e.response.status_code}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command("apikeys")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option("--key-words", default="", help="按 API Key 名称关键字搜索")
@click.option("--page", default=1, show_default=True, help="页码")
@click.option("--size", default=10, show_default=True, help="每页数量")
def list_apikeys(zone, owner, key_words, page, size):
    """查看当前账户的 iMaaS API Key 列表"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id

    try:
        data = _get(
            "/imaas/api/apikey",
            {"zone": zone, "owner": owner, "key_words": key_words, "page": page, "size": size},
        )
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"请求失败: HTTP {e.response.status_code}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command("metrics")
@click.option("--zone", default=None, help="区域标识")
@click.option("--owner", default=None, envvar="CORESHUB_USER_ID", help="账户 ID")
@click.option(
    "--start-time",
    required=True,
    type=int,
    help="查询开始时间（Unix 时间戳，秒）。与 end-time 间隔须在 1 分钟～30 天之间",
)
@click.option(
    "--end-time",
    default=None,
    type=int,
    help="查询结束时间（Unix 时间戳，秒，默认当前时间）",
)
@click.option(
    "--aggr-type",
    default="range",
    type=click.Choice(["range", "sum"]),
    show_default=True,
    help=(
        "数据汇总方式：\n"
        "  range（推荐）—— 时序折线，result[].sum 为区间总量\n"
        "  sum —— Prometheus increase()，滚动增量，一般不推荐"
    ),
)
@click.option("--api-key", default="", help="按 API Key 筛选（逗号分隔多个，留空=全部）")
@click.option("--model", default="", help="按模型名称筛选（逗号分隔多个，留空=全部）")
@click.option(
    "--token-type",
    default="",
    help="计量类型：input / output / cached（逗号分隔，留空=全部）",
)
@click.option(
    "--unit",
    default="",
    help="计费单位：token / count / seconds / words（逗号分隔，留空=全部）",
)
def token_metrics(zone, owner, start_time, end_time, aggr_type, api_key, model, token_type, unit):
    """查询 iMaaS 用量统计数据（Token / 次数 / 时长 / 字数）"""
    zone = zone or get_default_zone()
    owner = owner or settings.user_id
    end_time = end_time or int(_time.time())

    time_range = end_time - start_time
    if time_range < 60 or time_range > 3600 * 24 * 30:
        print(
            f"[错误] 时间范围须在 1 分钟～30 天之间，当前间隔 {time_range} 秒",
            file=sys.stderr,
        )
        sys.exit(1)

    params = {
        "zone": zone,
        "owner": owner,
        "start_time": start_time,
        "end_time": end_time,
        "aggr_type": aggr_type,
    }
    if api_key:
        params["api_key"] = api_key
    if model:
        params["model"] = model
    if token_type:
        params["token_type"] = token_type
    if unit:
        params["unit"] = unit

    try:
        data = _get("/imaas/api/metrics/tokens", params)
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
