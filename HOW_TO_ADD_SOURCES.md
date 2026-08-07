# 怎么加新新闻源（萨赫勒版）

## 改 `sources.json` 就行

文件结构：

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

**已配置的 9 个分类**：
- `国际媒体`：France 24 / Africanews / Al Jazeera / DW / BBC / Guardian / Le Monde / CNN / VOA / Africa Report / Premium Times / Africa-Press 等 15 个
- `萨赫勒专题`：Sahelien（法/英）· Sahel Express · Kéwoulo
- `RFI 双语`：RFI 8 国频道 × 英法双语 = 12 个
- `区域聚合`：AllAfrica 西非
- `马里` / `布基纳法索` / `尼日尔` / `乍得` / `塞内加尔`：各国本地媒体

可以直接加新分类（比如 `几内亚` / `毛里塔尼亚` / `科特迪瓦`）。

---

## 推荐添加更多源

### 国际组织 / 智库
- ISS Africa（智库分析）：`https://issafrica.org/feed`
- ACLED 武装冲突数据：`https://acleddata.com/feed/`
- Crisis Group：`https://www.crisisgroup.org/rss/region/sahel.xml`

### 各国本地源（已知有 RSS 的）

| 国家 | 推荐源 |
|---|---|
| 马里 | Maliweb, Kibaru, Mali Actu |
| 布基纳法索 | Sidwaya, LeFaso, Burkina24 |
| 尼日尔 | Niamey Info, Tamtaminfo, ActuNiger, Le Sahel |
| 乍得 | Alwihda Info, Tchadinfos |
| 毛里塔尼亚 | Sahara Media, Cridem, AMI |
| 塞内加尔 | Seneweb, Le Soleil, Walf |
| 几内亚 | Guinéenews, Mosaiqueguinee |
| 科特迪瓦 | Fraternité Matin, Abidjan.net |
| 贝宁 | Le Matinal, La Nouvelle Tribune |
| 冈比亚 | Foroyaa, The Point |
| 苏丹 | Sudan Tribune, Radio Dabanga |

**注意**：很多本地网站没有 RSS。可以去网站底部找 📡 图标，或者在谷歌搜「`网站名 RSS`」。

---

## 怎么找 RSS 地址

**方法 1：直接搜**
谷歌搜：`网站名 + RSS`，比如 `Burkina24 RSS feed`

**方法 2：看网站源码**
打开网站，在浏览器里按 F12（或右键查看网页源代码）搜 `application/rss+xml`

**方法 3：用 rss.app**
打开 https://rss.app/ ，输入网站 URL，自动找

**方法 4：找网站底部**
很多新闻网站底部有橙色 📡 图标

---

## 测试新加的源能不能跑

拿到 RSS URL 后，本地测试一下：

```bash
# 在项目目录里
python -c "
import feedparser, requests
r = requests.get('粘贴URL', timeout=10)
print('HTTP', r.status_code, 'size', len(r.content))
d = feedparser.parse(r.content)
print('条目数', len(d.entries))
print('第一条:', d.entries[0].title if d.entries else 'NONE')
"
```

- 看到 "HTTP 200" + "条目数 > 5" 就算可用
- 如果 "HTTP 404" 或 "条目数 0"，换别家的源

---

## 改完生效

1. 保存 `sources.json`
2. 打开 GitHub Desktop
3. 左下角 Summary 填 `update sources`（随便写）
4. 点 **「Commit to main」**
5. 右上角 **「Push origin」**
6. 等 2-3 分钟，网站自动更新
7. 或直接打开 Actions → Daily News Briefing → Run workflow 立刻看结果

---

## ⚠️ 注意事项

- **JSON 格式严格**：双引号、逗号不能错
- 改完可以用 https://www.json.cn/ 验证格式
- 改坏了删掉对应大括号/方括号的一段就行
- **加太多源可能让 AI 总结超 token 上限**：建议每个源最多 5-8 条，单次总结总条目 ≤ 200 条
- 当前默认 `max_items = 8`，可以在 sources.json 里某条上加 `"max_items": 15` 单独调整

---

**遇到问题截给我，我帮你看。**
