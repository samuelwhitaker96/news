"""AI 总结：调用 DeepSeek 把英文新闻翻译+总结成中文简报"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).parent.parent
CONTENT_DIR = ROOT / "content"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


def call_deepseek(prompt: str, system: str, api_key: str) -> str:
    """调用 DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }
    r = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()


def summarize_category(category: str, items: list[dict], api_key: str) -> str:
    """总结一个分类下的所有新闻"""
    if not items:
        return f"## {category}\n\n今日暂无重要新闻。\n"

    # 把新闻喂给 AI
    news_text = ""
    for i, item in enumerate(items, 1):
        title = item["title"]
        summary = item["summary"][:300]
        news_text += f"{i}. **{title}**\n   {summary}\n   链接: {item['link']}\n\n"

    system_prompt = """你是一位专业的中文新闻编辑。用户会给你一组同一分类（国际/科技）的英文新闻，
你的任务是：
1. 翻译成中文
2. 挑选最重要的 3-5 条
3. 每条用 1-2 句话总结核心内容
4. 重要程度用 1-3 个 🔥 标记
5. 给出原文链接

输出格式（严格遵守 Markdown）：
## [分类]

### 🔥🔥🔥 [翻译后的标题]
[1-2 句中文总结]
> 原文：[link]

### 🔥🔥 [翻译后的标题]
[1-2 句中文总结]
> 原文：[link]

### 🔥 [翻译后的标题]
[1-2 句中文总结]
> 原文：[link]

不要编造新闻。如果某条新闻信息不全，跳过它。"""

    user_prompt = f"以下是 {category} 分类下今天的新闻：\n\n{news_text}"

    try:
        return call_deepseek(user_prompt, system_prompt, api_key)
    except Exception as e:
        print(f"  ! DeepSeek error: {e}")
        # 失败时回退到原文展示
        lines = [f"## {category}\n"]
        for item in items[:5]:
            lines.append(f"### {item['title']}")
            lines.append(f"{item['summary'][:200]}")
            lines.append(f"> 原文：{item['link']}\n")
        return "\n".join(lines)


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("[ERROR] DEEPSEEK_API_KEY not set")
        print("Get one at https://platform.deepseek.com/ and run:")
        print('  setx DEEPSEEK_API_KEY "sk-你的key"')
        return 1

    # 找今天的原始数据
    today = datetime.now().strftime("%Y-%m-%d")
    raw_path = CONTENT_DIR / f"{today}-raw.json"
    if not raw_path.exists():
        print(f"[ERROR] No raw data: {raw_path}")
        print("Run fetch_rss.py first")
        return 1

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    by_category = raw.get("by_category", {})

    print(f"Summarizing {sum(len(v) for v in by_category.values())} items...")

    # 写标题和前言
    total = sum(len(v) for v in by_category.values())
    parts = [
        f"# 每日新闻简报 · {today}",
        "",
        f"> 自动整理于 {datetime.now().strftime('%H:%M')} · 共 {total} 条新闻",
        "",
    ]

    # 按分类处理
    for category in ["国际", "科技", "财经", "其他"]:
        items = by_category.get(category, [])
        if not items:
            continue
        print(f"  [{category}] {len(items)} items")
        result = summarize_category(category, items, api_key)
        parts.append(result)
        parts.append("")

    # 收尾
    parts.append("---")
    parts.append("")
    parts.append("*由 DeepSeek AI 自动整理 · 数据来源：BBC / Reuters / NYT / TechCrunch / The Verge*")

    out_path = CONTENT_DIR / f"{today}.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"\nDone. Written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
