# 怎么加新新闻源

## 你只需要改一个文件

**`sources.json`** —— 这个文件管理所有新闻源。

---

## 文件结构（很简单）

```json
{
  "分类名": [
    {
      "name": "网站名字",
      "url": "RSS 订阅地址",
      "description": "（可选）简单说明"
    }
  ]
}
```

每个**分类**是一个标题（比如"国际"、"科技"、"财经"），下面是一个**列表**，每项是一个网站。

---

## 怎么加

**加一个网站**：在某个分类下加一项，比如：

```json
{
  "国际": [
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "NYT World", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"}
  ]
}
```

**加一个分类**：直接写一个新标题：

```json
{
  "国际": [...],
  "科技": [...],
  "财经": [...],
  "体育": [
    {"name": "ESPN", "url": "https://..."}
  ]
}
```

**删一个网站**：直接把那行删了

**改抓取数量**：加 `"max_items": 数字`（默认 8）

```json
{"name": "Hacker News", "url": "https://hnrss.org/frontpage", "max_items": 15}
```

---

## 怎么找 RSS 地址？

**方法 1：直接搜**
谷歌搜：`网站名 + RSS`，比如 `Bloomberg RSS feed`

**方法 2：看网站底部**
很多新闻网站底部有橙色 📡 RSS 图标，右键 → 复制链接

**方法 3：用这个神器网站**
打开 https://rss.app/ ，输入新闻网站 URL，自动帮你找

---

## 常用 RSS 地址（直接复制）

### 国际综合
- BBC World: `http://feeds.bbci.co.uk/news/world/rss.xml`
- BBC Top Stories: `http://feeds.bbci.co.uk/news/rss.xml`
- NYT World: `https://rss.nytimes.com/services/xml/rss/nyt/World.xml`
- Guardian World: `https://www.theguardian.com/world/rss`
- Reuters: `https://feeds.reuters.com/Reuters/worldNews`

### 科技
- TechCrunch: `https://techcrunch.com/feed/`
- The Verge: `https://www.theverge.com/rss/index.xml`
- Hacker News: `https://hnrss.org/frontpage`
- Ars Technica: `https://feeds.arstechnica.com/arstechnica/index`
- Wired: `https://www.wired.com/feed/rss`
- Engadget: `https://www.engadget.com/rss.xml`

### 财经
- FT Home: `https://www.ft.com/rss/home`
- Bloomberg Markets: `https://feeds.bloomberg.com/markets/news.rss`
- WSJ Markets: `https://feeds.a.dj.com/rss/RSSMarkets.xml`
- Investing.com: `https://www.investing.com/rss/news.rss`

### 体育
- ESPN: `https://www.espn.com/espn/rss/news`
- BBC Sport: `http://feeds.bbci.co.uk/sport/rss.xml`
- The Athletic: `https://theathletic.com/rss/feed.xml`

### AI / ML
- MIT Tech Review AI: `https://www.technologyreview.com/topic/artificial-intelligence/feed`
- OpenAI Blog: `https://openai.com/blog/rss.xml`
- Google DeepMind: `https://deepmind.google/blog/rss.xml`

### 加密货币
- CoinDesk: `https://www.coindesk.com/arc/outboundfeeds/rss/`
- Cointelegraph: `https://cointelegraph.com/rss`

---

## ⚠️ 注意事项

1. **JSON 格式**很严格：
   - 每行末尾的逗号**不能少**（最后一行除外）
   - 字符串必须用**英文双引号** `"`，不能用单引号
   - 大括号 `{ }` 和方括号 `[ ]` 必须成对

2. **改错语法会报错**：
   - 打开 https://www.json.cn/ 把内容粘进去，能帮你检查格式

3. **改完生效步骤**：
   1. 保存 sources.json
   2. 打开 GitHub Desktop
   3. 左侧会显示改动
   4. 底部 Summary 填 `update sources`（随便写）
   5. 点 **「Commit to main」**
   6. 右上角点 **「Push origin」**
   7. 等 2-3 分钟，网站自动更新

---

## 改完想测试

可以在 PowerShell 跑：

```powershell
cd "C:\Users\green\WorkBuddy AI\2026-08-07-09-47-11\news-briefing"
python scripts\fetch_rss.py
```

会立刻抓取并显示结果，看看新加的源有没有东西。

---

**遇到问题截给我**，我帮你看。
