# 每日新闻简报

> 自动从国外新闻网站抓取要闻，AI 整理成中文简报，每天更新。

## 项目结构

```
news-briefing/
├── .github/workflows/daily.yml   # GitHub Actions 定时任务
├── scripts/
│   ├── fetch_rss.py              # RSS 抓取
│   ├── summarize.py              # DeepSeek 总结
│   └── build_site.py             # 静态网站生成
├── content/                      # 每日简报（自动生成）
├── site/                         # 生成的网站（部署用）
├── requirements.txt
└── README.md
```

## 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 抓取 RSS（不需要 key）
python scripts/fetch_rss.py

# 3. AI 总结（需要 DeepSeek API key）
export DEEPSEEK_API_KEY="sk-你的key"
python scripts/summarize.py

# 4. 生成网站
python scripts/build_site.py

# 5. 预览
python -m http.server --directory site 8000
# 浏览器打开 http://localhost:8000
```

## 部署到 GitHub Pages

1. 把代码 push 到 GitHub 仓库
2. 仓库 Settings → Pages → Source 选 "GitHub Actions"
3. 仓库 Settings → Secrets and variables → Actions → 新建：
   - Name: `DEEPSEEK_API_KEY`
   - Value: 你的 DeepSeek key
4. 等首次 workflow 跑完（可手动触发）
5. 访问 `https://<用户名>.github.io/<仓库名>/`

## 数据源

| 分类 | 源 |
|---|---|
| 国际 | BBC, Reuters, NYT |
| 科技 | TechCrunch, The Verge |

## 自定义

### 加新源

编辑 `scripts/fetch_rss.py` 的 `SOURCES` 字典：

```python
SOURCES = {
    "财经": [
        ("Bloomberg", "https://..."),
    ],
}
```

### 改总结风格

编辑 `scripts/summarize.py` 的 `summarize_items` 函数里的 system prompt。

### 改更新频率

编辑 `.github/workflows/daily.yml` 的 cron 表达式。

## 成本

- GitHub Pages + Actions: 免费（每月 2000 分钟）
- DeepSeek API: 约 0.001 元/次总结

## License

MIT
