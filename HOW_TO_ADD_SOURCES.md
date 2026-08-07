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

**已配置的分类**：
- `国际媒体`：France 24 / Africanews / Al Jazeera / DW
- `区域聚合`：AllAfrica / Sahel Express
- `本地媒体`：Mali Actu

可以直接加新分类，比如 `乍得媒体` / `布基纳法索媒体`。

---

## 推荐添加的萨赫勒源

### 萨赫勒综合性
- AllAfrica Sahel 频道：`https://allafrica.com/tools/headlines/rdf/sahel/headlines.rdf`（可能需要试）
- ISS Africa（智库分析）：`https://issafrica.org/feed`
- Crisis Group Sahel：`https://www.crisisgroup.org/rss/region/sahel.xml`

### 各国本地源
| 国家 | 推荐源 |
|---|---|
| 马里 | Mali Actu, Maliweb, Studio Tamani |
| 布基纳法索 | Lefaso.net, Burkina24 |
| 尼日尔 | Niamey Info, Tamtaminfo, ActuNiger |
| 乍得 | Alwihda Info, Tchadinfos |
| 毛里塔尼亚 | Sahara Media, Cridem |
| 塞内加尔 | Seneweb, Le Soleil |
| 几内亚 | Guinéenews, Mosaiqueguinee |

**注意**：很多本地网站没有 RSS。可以去网站底部找 📡 图标，或者在谷歌搜「`网站名 RSS`」。

---

## 怎么找 RSS 地址

**方法 1：直接搜**
谷歌搜：`网站名 + RSS`，比如 `Burkina24 RSS feed`

**方法 2：用 rss.app**
打开 https://rss.app/ ，输入网站 URL，自动找

**方法 3：找网站底部**
很多新闻网站底部有橙色 📡 图标

---

## 改完生效

1. 保存 `sources.json`
2. 打开 GitHub Desktop
3. 左下角 Summary 填 `update sources`（随便写）
4. 点 **「Commit to main」**
5. 右上角 **「Push origin」**
6. 等 2-3 分钟，网站自动更新

---

## ⚠️ 注意事项

- JSON 格式严格：双引号、逗号不能错
- 改完可以用 https://www.json.cn/ 验证格式
- 改坏了删掉对应大括号/方括号的一段就行
- 加太多源可能让 AI 总结超 token 上限，建议总数 ≤ 20

---

**遇到问题截给我，我帮你看。**
