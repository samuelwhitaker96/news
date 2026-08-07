# 部署到 GitHub Pages（24 小时自动更新）

> 完成这一步步后，网站会每天自动更新，你不用再管。

## 第一步：注册 GitHub 账号（如果还没有）

打开 https://github.com/signup ，用邮箱注册，验证邮箱。

## 第二步：创建仓库

1. 登录后点右上角 `+` → `New repository`
2. Repository name 填：`news-briefing`（或你喜欢的名字）
3. 选 `Public`（公开仓库 Pages 才能用）
4. **不要**勾选 "Add a README file"
5. 点 `Create repository`
6. 复制仓库地址（形如 `https://github.com/你的用户名/news-briefing.git`）

## 第三步：把代码推上去

打开 PowerShell，执行：

```powershell
cd "C:\Users\green\WorkBuddy AI\2026-08-07-09-47-11\news-briefing"

git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/news-briefing.git
git push -u origin main
```

（把 `你的用户名` 替换成你 GitHub 的用户名）

如果弹出登录框，输入 GitHub 用户名密码。如果开了两步验证，用 Personal Access Token（PAT）代替密码：
- 头像 → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
- 勾选 `repo` 全选
- 复制 token，粘贴到登录框

## 第四步：配置 DeepSeek API Key

1. 打开仓库页面 → `Settings` → `Secrets and variables` → `Actions`
2. 点 `New repository secret`
3. Name: `DEEPSEEK_API_KEY`
4. Value: 粘贴你的 DeepSeek key（`sk-xxx...`）
5. 点 `Add secret`

## 第五步：开启 GitHub Pages

1. 仓库 `Settings` → `Pages`
2. Source: 选 `GitHub Actions`
3. 不用动其他选项，保存

## 第六步：手动跑一次（首次）

1. 仓库页面点 `Actions` 标签
2. 左侧选 `Daily News Briefing`
3. 右侧 `Run workflow` → 绿色按钮
4. 等待 2-3 分钟跑完

跑完后访问：`https://你的用户名.github.io/news-briefing/`

## 第七步：搞定

- 每天 UTC 0 点（北京时间早上 8 点）自动跑
- 不用你操作

---

## 常见问题

**Q: 推送时提示要输入密码？**
A: 填 Personal Access Token，不是 GitHub 密码。

**Q: Actions 跑失败？**
A: 点进失败的任务看日志。最常见是 DeepSeek key 没设对。

**Q: 想换更新频率？**
A: 编辑 `.github/workflows/daily.yml` 的 `cron` 那一行（默认 `0 0 * * *` = 每天 0 点）。

**Q: 想加新新闻源？**
A: 编辑 `scripts/fetch_rss.py` 的 `SOURCES` 字典，添加源和 RSS 地址。

**Q: 国内访问 GitHub Pages 慢？**
A: 可以用 CDN 加速（Cloudflare），或先用我之前部署的 CloudStudio 链接。
