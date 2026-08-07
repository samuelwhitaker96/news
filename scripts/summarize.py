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

    system_prompt = """你是一位专业的国际新闻编辑，专门关注西非萨赫勒地区。用户会给你一组同一分类的新闻，
你的任务是：
1. 翻译成中文
2. 挑选最重要的 3-5 条（优先关注萨赫勒地区——马里、布基纳法索、尼日尔、乍得、毛里塔尼亚、塞内加尔、几内亚）
3. 每条用 1-2 句话总结核心内容
4. 重要程度用 1-3 个 🔥 标记（萨赫勒本地新闻优先于泛非/国际报道）
5. 给出原文链接
6. 重点关注：武装冲突/恐袭、政变、地区安全联盟（AES）、西方撤军、与俄罗斯/中国合作、人道危机、粮食安全

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

不要编造新闻。如果某条新闻信息不全或与萨赫勒无关，跳过它。"""

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

    total = sum(len(v) for v in by_category.values())
    print(f"Summarizing {total} items in {len(by_category)} categories...")

    # 写标题和前言
    parts = [
        f"# 西非萨赫勒新闻简报 · {today}",
        "",
        f"> 自动整理于 {datetime.now().strftime('%H:%M')} · 共 {total} 条新闻",
        "",
    ]

    # 按分类处理：遍历 sources.json 里的实际分类顺序，缺的跳过
    for category, items in by_category.items():
        if not items:
            continue
        print(f"  [{category}] {len(items)} items")
        result = summarize_category(category, items, api_key)
        parts.append(result)
        parts.append("")

    # 收尾
    parts.append("---")
    parts.append("")
    parts.append("*由 DeepSeek AI 自动整理 · 关注西非萨赫勒地区：马里 / 布基纳法索 / 尼日尔 / 乍得 / 毛里塔尼亚 / 塞内加尔 等*")

    out_path = CONTENT_DIR / f"{today}.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"\nDone. Written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
