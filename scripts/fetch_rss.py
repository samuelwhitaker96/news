"""RSS 抓取：从多个新闻源拉取最近 24 小时的新闻"""
import feedparser
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from html import unescape

ROOT = Path(__file__).parent.parent
SOURCES_FILE = ROOT / "sources.json"
DEFAULT_MAX_PER_SOURCE = 8
HOURS_WINDOW = 24


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


def load_sources() -> dict:
    """加载源配置"""
    if not SOURCES_FILE.exists():
        print(f"[WARN] {SOURCES_FILE} 不存在，使用默认源")
        return {
            "国际": [
                {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
            ],
        }
    data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    # 过滤掉以 _ 开头的元数据键
    return {k: v for k, v in data.items() if not k.startswith("_")}


def fetch_source(name: str, url: str, cutoff: datetime, max_items: int) -> list[dict]:
    """抓取单个源"""
    print(f"  [{name}] {url}")
    try:
        feed = feedparser.parse(url, agent="news-briefing/1.0")
    except Exception as e:
        print(f"    ! fetch error: {e}")
        return []

    items = []
    for entry in feed.entries[:max_items * 2]:
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
        if len(items) >= max_items:
            break

    print(f"    -> {len(items)} items")
    return items


def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=HOURS_WINDOW)
    sources = load_sources()
    print(f"Fetching news since {cutoff.isoformat()}")
    print(f"Sources loaded: {sum(len(v) for v in sources.values())} feeds in {len(sources)} categories\n")

    by_category: dict[str, list[dict]] = {}
    for category, feeds in sources.items():
        by_category[category] = []
        for feed in feeds:
            name = feed["name"]
            url = feed["url"]
            max_items = feed.get("max_items", DEFAULT_MAX_PER_SOURCE)
            by_category[category].extend(fetch_source(name, url, cutoff, max_items))

    # 跨所有源去重：相同标题前缀（去标点/空格后）只保留第一条
    seen_keys: set[str] = set()
    dedup_total = 0
    for category in by_category:
        deduped: list[dict] = []
        for it in by_category[category]:
            key = re.sub(r"[\s\W_]+", "", it["title"].lower())[:60]
            if not key:
                continue
            if key in seen_keys:
                dedup_total += 1
                continue
            seen_keys.add(key)
            deduped.append(it)
        by_category[category] = deduped

    if dedup_total:
        print(f"\n跨源去重：移除 {dedup_total} 条重复新闻（保留较早出现的源）")

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
