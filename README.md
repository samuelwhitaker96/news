# 每日新闻简报 · 西非萨赫勒版

> 自动从 42 个新闻媒体抓取要闻，AI（DeepSeek）整理成中文简报，每天北京时间 8 点更新 + 可选推送到微信 / 邮箱。

## 这个项目做什么？

每天 UTC 0:00（北京时间 8:00）自动跑：

1. **抓取**：从 42 个萨赫勒 / 西非 / 国际媒体的 RSS 源，抓取最新新闻
2. **AI 整理**：用 DeepSeek 把英文 / 法文新闻翻译成中文，按议题分类、要点提炼
3. **生成网站**：渲染成纯静态 HTML（GitHub Pages 部署）
4. **推送**（可选）：通过 9 种渠道推送到你的微信 / 企业微信 / Telegram / 邮件等

## 项目结构

```
news-briefing/
├── .github/workflows/daily.yml   # GitHub Actions 定时任务
├── scripts/
│   ├── fetch_rss.py              # 1️⃣ RSS 抓取 + 跨源去重
│   ├── summarize.py              # 2️⃣ DeepSeek AI 总结
│   ├── build_site.py             # 3️⃣ 静态网站生成
│   └── push.py                   # 4️⃣ 多渠道推送（9 种）
├── sources.json                  # 42 个 RSS 源配置（用户可编辑）
├── content/                      # 每日简报 markdown（自动生成）
├── site/                         # 生成的 HTML（部署用）
├── HOW_TO_ADD_SOURCES.md         # 怎么加 / 减 RSS 源
├── HOW_TO_SETUP_PUSH.md          # 怎么配置推送
├── requirements.txt
└── README.md
```

## 本地运行

```bash
# 1. 安装依赖（已装好可跳过）
pip install -r requirements.txt

# 2. 抓 RSS（不需要 key）
python scripts/fetch_rss.py

# 3. AI 总结（需要 DeepSeek API key）
export DEEPSEEK_API_KEY="sk-你的key"
python scripts/summarize.py

# 4. 生成网站
python scripts/build_site.py

# 5.（可选）推送
export SERVERCHAN_KEY="SCT..."      # 例如推微信
python scripts/push.py

# 6. 预览
python -m http.server --directory site 8000
# 浏览器打开 http://localhost:8000
```

## 部署到 GitHub Pages

1. 把代码 push 到 GitHub 仓库
2. 仓库 Settings → Pages → Source 选 "GitHub Actions"
3. 仓库 Settings → Secrets and variables → Actions → 新建：
   - `DEEPSEEK_API_KEY`：你的 DeepSeek key（**必须**，否则 AI 总结会失败）
4. （可选）添加推送密钥，详见 `HOW_TO_SETUP_PUSH.md`
5. 等首次 workflow 跑完（也可手动 Run workflow）
6. 访问 `https://<用户名>.github.io/<仓库名>/`

## 数据源（42 个）

| 分类 | 数量 | 代表源 |
|---|---|---|
| 国际媒体 | 15 | BBC Africa · France 24（法/英/西）· Al Jazeera · Le Monde · CNN · VOA · The Guardian |
| 萨赫勒专题 | 4 | Sahelien（法/英）· Sahel Express · Kéwoulo |
| RFI 双语 | 12 | RFI 非洲总览 · 8 个国家频道（马里/布基纳/尼日尔/乍得/毛里塔尼亚/塞内加尔/几内亚）× 英法双语 |
| 区域聚合 | 1 | AllAfrica 西非 |
| 马里 | 2 | Studio Tamani · Mali Actu |
| 布基纳法索 | 4 | Lefaso.net · Burkina24 · Journal du Faso · Le Pays |
| 尼日尔 | 2 | Le Sahel（官方日报）· Niger Inter |
| 乍得 | 2 | Alwihda Info · Tchadinfos |
| 塞内加尔 | 1 | Le Soleil（官方日报） |

加 / 减源：直接编辑 `sources.json`，详见 `HOW_TO_ADD_SOURCES.md`。

## 自定义

### 加新源
编辑 `sources.json`：

```json
{
  "我的分类": [
    {"name": "网站名字", "url": "RSS 网址", "description": "说明"}
  ]
}
```

### 改 AI 总结风格
编辑 `scripts/summarize.py` 里 `summarize_category()` 的 `system_prompt`（关注议题、字数、火苗等级等）。

### 改推送渠道 / 改频率
- 推送渠道：详见 `HOW_TO_SETUP_PUSH.md`
- 频率：编辑 `.github/workflows/daily.yml` 的 cron 表达式

## 推送渠道（9 种，可选）

| 渠道 | 国内/国外 | 难度 |
|---|---|---|
| **Server酱**（推微信） | 国内 | ⭐ |
| **PushPlus**（推微信公众号） | 国内 | ⭐ |
| **企业微信群机器人** | 国内 | ⭐⭐ |
| **钉钉群机器人** | 国内 | ⭐⭐ |
| **飞书机器人** | 国内 | ⭐⭐ |
| Discord | 国外 | ⭐ |
| Telegram | 国外 | ⭐⭐ |
| Bark（iOS） | 国内/国外 | ⭐ |
| SMTP Email（QQ / 163 / Gmail） | 国内/国外 | ⭐⭐ |

详见 **`HOW_TO_SETUP_PUSH.md`**。

## 成本

- **GitHub Pages + Actions**：完全免费（每月 2000 分钟）
- **DeepSeek API**：约 0.01 元 / 次总结（每天 1 次）
- **推送**：所有列出渠道全部免费

## License

MIT
