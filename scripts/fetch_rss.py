"""RSS 抓取：从多个新闻源拉取最近 24 小时的新闻"""
import feedparser
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from html import unescape

# 新闻源配置
SOURCES = {
    "国际": [
        ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
        ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
        ("NYT World", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ],
    "科技": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ],
}

MAX_PER_SOURCE = 8  # 每个源最多取多少条
HOURS_WINDOW = 24    # 抓最近多少小时


def clean_html(text: str) -> str:
    """去除 HTML 标签和实体"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:800]  # 限制长度


def parse_date(entry) -> datetime | None:
    """解析 RSS 条目的发布时间"""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        v = getattr(entry, attr, None)
        if v:
            try:
                return datetime(*v[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def fetch_source(name: str, url: str, cutoff: datetime) -> list[dict]:
    """抓取单个源"""
    print(f"  [{name}] {url}")
    try:
        feed = feedparser.parse(url, agent="news-briefing/1.0")
    except Exception as e:
        print(f"    ! fetch error: {e}")
        return []

    items = []
    for entry in feed.entries[:MAX_PER_SOURCE * 2]:
        pub = parse_date(entry)
        if pub and pub < cutoff:
            continue  # 太旧
        items.append({
            "title": clean_html(entry.get("title", "")),
            "summary": clean_html(entry.get("summary", "") or entry.get("description", "")),
            "link": entry.get("link", ""),
            "published": pub.isoformat() if pub else None,
            "source": name,
        })
        if len(items) >= MAX_PER_SOURCE:
            break

    print(f"    -> {len(items)} items")
    return items


def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=HOURS_WINDOW)
    print(f"Fetching news since {cutoff.isoformat()}")

    by_category: dict[str, list[dict]] = {}
    for category, sources in SOURCES.items():
        by_category[category] = []
        for name, url in sources:
            by_category[category].extend(fetch_source(name, url, cutoff))

    out_dir = Path(__file__).parent.parent / "content"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = now.strftime("%Y-%m-%d")
    out_path = out_dir / f"{today}-raw.json"

    payload = {
        "fetched_at": now.isoformat(),
        "cutoff": cutoff.isoformat(),
        "by_category": by_category,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(v) for v in by_category.values())
    print(f"\nDone. {total} items written to {out_path}")


if __name__ == "__main__":
    main()
