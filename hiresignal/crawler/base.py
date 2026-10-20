"""通用抓取工具：requests + BeautifulSoup。"""

import re

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def fetch(url: str, timeout: int = 15) -> str:
    """抓取网页，返回 HTML 文本。"""
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def parse(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def clean_text(fragment) -> str:
    """把 HTML 片段转成纯文本并压缩空白。"""
    soup = BeautifulSoup(str(fragment), "lxml")
    return re.sub(r"\s+", " ", soup.get_text()).strip()
