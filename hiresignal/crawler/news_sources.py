"""融资新闻源：投资界（pedaily.cn）。"""

from .base import fetch, parse, clean_text

# 排除词：投资动态/公告类标题，不算「公司完成融资」事件
EXCLUDE_HINTS = ("基金", "遴选", "公告", "拟出资", "周报", "盘点", "榜单", "排名", "招引", "路演")


def is_funding_title(title: str) -> bool:
    """标题含「融资」且非基金/公告类，才算候选融资事件。"""
    if "融资" not in title:
        return False
    if any(k in title for k in EXCLUDE_HINTS):
        return False
    return True


class PedailySource:
    """投资界融资新闻源。"""

    id = "pedaily"
    name = "投资界"
    homepage = "https://www.pedaily.cn/"

    def list_articles(self, limit: int = 20) -> list[dict]:
        """从首页抓取融资新闻链接列表。返回 [{title, url}]。"""
        html = fetch(self.homepage)
        soup = parse(html)
        out = []
        seen = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "news.pedaily.cn" not in href:
                continue
            title = clean_text(a)
            if not title or not is_funding_title(title):
                continue
            if href in seen:
                continue
            seen.add(href)
            out.append({"title": title, "url": href})
            if len(out) >= limit:
                break
        return out

    def fetch_article(self, url: str) -> dict:
        """抓取详情页，返回 {title, text, url}。"""
        html = fetch(url)
        soup = parse(html)
        title = soup.title.get_text(strip=True) if soup.title else ""
        # 正文：投资界正文在 .news-content 或类似容器，兜底取 body
        content = soup.find("div", class_=lambda c: c and "content" in c)
        if content is None:
            content = soup.body
        text = clean_text(content)
        return {"title": title, "text": text, "url": url}
