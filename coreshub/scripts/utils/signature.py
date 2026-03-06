"""
QingCloud / CoreshHub API 签名工具
"""

import base64
import hashlib
import hmac
from collections import OrderedDict
from hashlib import sha256
from urllib import parse


def hex_encode_md5_hash(data: str = "") -> str:
    raw = data.encode("utf-8") if data else b""
    return hashlib.md5(raw).hexdigest()


def get_signature(method: str, url: str, ak: str, sk: str, params: dict) -> str:
    """
    计算 QingCloud 风格的 HMAC-SHA256 签名，返回带签名的 query string。

    :param method: HTTP 方法，如 GET / POST
    :param url:    接口路径，如 /api/test
    :param ak:     Access Key ID
    :param sk:     Secret Key
    :param params: 请求参数字典
    :return:       带 signature 字段的 query string
    """
    if not url.endswith("/"):
        url += "/"

    params["access_key_id"] = ak

    sorted_param: OrderedDict = OrderedDict()
    for key in sorted(params.keys()):
        value = params[key]
        sorted_param[key] = sorted(value) if isinstance(value, list) else value

    url_param = parse.urlencode(sorted_param, safe="/", quote_via=parse.quote, doseq=True)
    string_to_sign = f"{method}\n{url}\n{url_param}\n{hex_encode_md5_hash()}"

    h = hmac.new(sk.encode("utf-8"), digestmod=sha256)
    h.update(string_to_sign.encode("utf-8"))
    sign = base64.b64encode(h.digest()).strip()

    signature = parse.quote_plus(parse.quote_plus(sign.decode()))
    return f"{url_param}&signature={signature}"
