"""静态网站生成：把每日简报渲染成 HTML"""
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
import markdown
from jinja2 import Template

ROOT = Path(__file__).parent.parent
CONTENT_DIR = ROOT / "content"
SITE_DIR = ROOT / "site"

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日新闻简报</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header>
  <h1>每日新闻简报</h1>
  <p class="subtitle">国际 · 科技 · AI 整理</p>
</header>
<nav>
  <a href="index.html">最新</a>
  <a href="archive.html">历史归档</a>
  <a href="about.html">关于</a>
</nav>
<main>
{{ content | safe }}
</main>
<footer>
  <p>由 DeepSeek 自动整理 · 数据来源：BBC / Reuters / NYT / TechCrunch / The Verge</p>
  <p>最后更新：{{ updated }}</p>
</footer>
</body>
</html>
"""

ARCHIVE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>归档 · 每日新闻简报</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header>
  <h1>归档</h1>
  <p class="subtitle">所有历史简报</p>
</header>
<nav>
  <a href="index.html">最新</a>
  <a href="archive.html">历史归档</a>
  <a href="about.html">关于</a>
</nav>
<main>
<ul class="archive-list">
{% for date in dates %}
  <li><a href="briefings/{{ date }}.html">{{ date }}</a></li>
{% endfor %}
</ul>
</main>
<footer>
  <p>由 DeepSeek 自动整理</p>
</footer>
</body>
</html>
"""

BRIEFING_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ date }} · 每日新闻简报</title>
<link rel="stylesheet" href="../styles.css">
</head>
<body>
<header>
  <h1>每日新闻简报</h1>
  <p class="subtitle">{{ date }}</p>
</header>
<nav>
  <a href="../index.html">最新</a>
  <a href="../archive.html">历史归档</a>
  <a href="../about.html">关于</a>
</nav>
<main>
<a href="../index.html" class="back">← 返回最新</a>
{{ content | safe }}
</main>
<footer>
  <p>由 DeepSeek 自动整理</p>
</footer>
</body>
</html>
"""

ABOUT_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>关于 · 每日新闻简报</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header>
  <h1>关于</h1>
  <p class="subtitle">本项目说明</p>
</header>
<nav>
  <a href="index.html">最新</a>
  <a href="archive.html">历史归档</a>
  <a href="about.html">关于</a>
</nav>
<main>
<h2>这是什么？</h2>
<p>一个每天自动从国外新闻网站抓取要闻，用 AI 整理成中文简报的网站。</p>

<h2>数据来源</h2>
<ul>
  <li><strong>国际</strong>：BBC、Reuters、纽约时报</li>
  <li><strong>科技</strong>：TechCrunch、The Verge</li>
</ul>
<p>通过 RSS 订阅获取，无人工干预。</p>

<h2>整理流程</h2>
<ol>
  <li>每天定时抓取所有源最近 24 小时的新闻</li>
  <li>用 DeepSeek AI 翻译成中文 + 提炼核心</li>
  <li>按主题分类，生成简报</li>
  <li>网站自动更新</li>
</ol>

<h2>更新频率</h2>
<p>每天 UTC 0 点（北京时间早上 8 点）自动更新。</p>

<h2>技术栈</h2>
<ul>
  <li>抓取：Python + feedparser</li>
  <li>AI：DeepSeek Chat API</li>
  <li>展示：纯 HTML + CSS</li>
  <li>定时：GitHub Actions</li>
  <li>部署：GitHub Pages</li>
</ul>
</main>
<footer>
  <p>由 DeepSeek 自动整理</p>
</footer>
</body>
</html>
"""

STYLES = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  line-height: 1.7;
  color: #1a1a1a;
  background: #fafafa;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
header {
  border-bottom: 2px solid #2563eb;
  padding-bottom: 16px;
  margin-bottom: 24px;
}
header h1 { font-size: 2em; color: #1e40af; }
header .subtitle { color: #6b7280; margin-top: 4px; }
nav {
  background: #f3f4f6;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  gap: 16px;
}
nav a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}
nav a:hover { text-decoration: underline; }
main h1 { font-size: 1.6em; margin: 24px 0 12px; color: #1e40af; }
main h2 { font-size: 1.3em; margin: 24px 0 12px; color: #1e40af;
          border-left: 4px solid #2563eb; padding-left: 12px; }
main h3 { font-size: 1.1em; margin: 16px 0 8px; color: #374151; }
main p, main li { margin: 8px 0; }
main ul, main ol { padding-left: 24px; }
main a { color: #2563eb; }
main blockquote {
  border-left: 4px solid #d1d5db;
  padding-left: 16px;
  color: #6b7280;
  font-style: italic;
  margin: 12px 0;
}
main code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: "SF Mono", Consolas, monospace;
  font-size: 0.9em;
}
footer {
  margin-top: 48px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  color: #9ca3af;
  font-size: 0.9em;
  text-align: center;
}
.archive-list { list-style: none; padding: 0; }
.archive-list li {
  padding: 12px 16px;
  margin: 8px 0;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}
.archive-list a {
  text-decoration: none;
  color: #1e40af;
  font-weight: 500;
}
.back {
  display: inline-block;
  margin-bottom: 16px;
  color: #6b7280;
  text-decoration: none;
}
.back:hover { color: #2563eb; }
@media (max-width: 600px) {
  body { padding: 12px; }
  header h1 { font-size: 1.5em; }
  nav { flex-wrap: wrap; }
}
"""


def render_index() -> Path:
    """渲染首页：显示最新一份简报"""
    briefings = sorted(CONTENT_DIR.glob("????-??-??.md"), reverse=True)
    template = Template(INDEX_TEMPLATE)
    if not briefings:
        content_html = "<p>还没有任何简报。首次运行会在 UTC 0 点自动生成。</p>"
        updated = "尚未生成"
    else:
        latest = briefings[0]
        md = latest.read_text(encoding="utf-8")
        content_html = markdown.markdown(
            md, extensions=["fenced_code", "tables", "toc"]
        )
        updated = latest.stem

    out = SITE_DIR / "index.html"
    out.write_text(
        template.render(content=content_html, updated=updated), encoding="utf-8"
    )
    return out


def render_archive() -> Path:
    """渲染归档页：所有简报日期"""
    dates = sorted(
        [p.stem for p in CONTENT_DIR.glob("????-??-??.md")], reverse=True
    )
    template = Template(ARCHIVE_TEMPLATE)
    out = SITE_DIR / "archive.html"
    out.write_text(template.render(dates=dates), encoding="utf-8")
    return out


def render_briefings() -> list[Path]:
    """为每份简报生成单独页面"""
    template = Template(BRIEFING_TEMPLATE)
    out_dir = SITE_DIR / "briefings"
    out_dir.mkdir(exist_ok=True)
    paths = []
    for md_file in sorted(CONTENT_DIR.glob("????-??-??.md"), reverse=True):
        md = md_file.read_text(encoding="utf-8")
        content_html = markdown.markdown(
            md, extensions=["fenced_code", "tables", "toc"]
        )
        out = out_dir / f"{md_file.stem}.html"
        out.write_text(
            template.render(date=md_file.stem, content=content_html),
            encoding="utf-8",
        )
        paths.append(out)
    return paths


def render_about() -> Path:
    out = SITE_DIR / "about.html"
    out.write_text(ABOUT_TEMPLATE, encoding="utf-8")
    return out


def main():
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    # 复制样式
    (SITE_DIR / "styles.css").write_text(STYLES, encoding="utf-8")

    print("Building site...")
    p1 = render_index()
    p2 = render_archive()
    p3 = render_about()
    p4 = render_briefings()

    print(f"  index:    {p1.relative_to(ROOT)}")
    print(f"  archive:  {p2.relative_to(ROOT)}")
    print(f"  about:    {p3.relative_to(ROOT)}")
    print(f"  briefings: {len(p4)} files")
    print("Done.")


if __name__ == "__main__":
    main()
