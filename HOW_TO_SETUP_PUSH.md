# 怎样把简报自动推送到你的微信 / QQ / 手机？

每天早上 8 点（北京时间），网站会自动更新一份简报。
如果你想**同步收到一份到自己的手机 / 微信 / 邮箱**，
只需在 GitHub 后台配置一个或多个"推送密钥"即可。

支持以下 9 种渠道，**任意组合**，没配的不发：

| 渠道 | 一句话说明 | 推荐度 |
|---|---|---|
| **Server酱** | 把消息推到你的**微信**（推荐小白） | ⭐⭐⭐⭐⭐ |
| **PushPlus** | 把消息推到你的**微信公众号** | ⭐⭐⭐⭐ |
| **企业微信群机器人** | 推到企业微信群（无需 APP） | ⭐⭐⭐⭐ |
| **钉钉群机器人** | 推到钉钉群（无需 APP） | ⭐⭐⭐⭐ |
| **飞书机器人** | 推到飞书群（无需 APP） | ⭐⭐⭐⭐ |
| **Telegram Bot** | 推到 Telegram 聊天 / 群 | ⭐⭐⭐ |
| **Bark** | 推到 iPhone（免费 App） | ⭐⭐⭐ |
| **Discord Webhook** | 推到 Discord 服务器频道 | ⭐⭐ |
| **Email (SMTP)** | 推到任意邮箱（QQ / 163 / Gmail） | ⭐⭐⭐ |

下面分两步教你：**① 拿到推送密钥 ② 在 GitHub 后台配上密钥**。

---

## 总流程（所有渠道都一样）

```
拿渠道的密钥（一串字符）  ──>  粘到 GitHub 仓库的 Secrets  ──>  等下一次 8:00 自动推送
                              （或手动跑一次 workflow 测试）
```

### 第 1 步：打开 Secrets 页面

1. 浏览器打开 https://github.com/samuelwhitaker96/news/settings/secrets/actions
   > 把 `samuelwhitaker96/news` 改成你自己的仓库地址。

2. 点右上角 **"New repository secret"** 按钮。

3. 在 **Name** 里填下面表格里的"变量名"（比如 `SERVERCHAN_KEY`）。

4. 在 **Secret** 里填你拿到的密钥（一串字符）。

5. 点 **"Add secret"** 按钮。

6. 重复以上步骤，添加你想用的所有渠道的密钥。
   > **没填的渠道会自动跳过，不会报错。**

### 第 2 步：手动测试一次

回到 https://github.com/samuelwhitaker96/news/actions

1. 点左边 **"Daily News Briefing"**
2. 右边点 **"Run workflow"** → 绿色按钮 **"Run workflow"**
3. 等 1-3 分钟，看日志底部是否出现 `✅ X 个渠道推送成功`

---

## 渠道 ① Server酱（推微信，最推荐）

免费、无需企业认证、个人微信就能收。

| 变量名 | 值 |
|---|---|
| `SERVERCHAN_KEY` | 你的 SendKey |

**如何拿 SendKey：**

1. 打开 https://sct.ftqq.com/ 用微信扫码登录
2. 点左边 **"发送消息"**
3. 在 **"SendKey"** 一栏直接复制（长得像 `SCT27xxxxx...`）
4. 把这个字符串填到 GitHub Secret `SERVERCHAN_KEY`
5. 加完后扫码测试一下能否收到推送

> 免费版每日 5 条上限。本简报每天 1 条，**绝对够用**。

---

## 渠道 ② PushPlus（推到"微信公众号"）

无需任何认证，只需要手机号注册。可以推到你的微信"文件传输助手"。

| 变量名 | 值 |
|---|---|
| `PUSHPLUS_TOKEN` | 你的 token |

**如何拿 token：**

1. 打开 https://www.pushplus.plus/ 用微信扫码注册
2. 登录后首页直接看到你的 **token**（一长串字符）
3. 复制，填到 GitHub Secret `PUSHPLUS_TOKEN`

> 免费用户每天 200 条额度，**够用**。

---

## 渠道 ③ 企业微信群机器人（无需 App）

需要有一个企业微信群。

| 变量名 | 值 |
|---|---|
| `WECOM_WEBHOOK_URL` | 群的 webhook URL |

**如何拿 webhook：**

1. 打开企业微信 → 进入某个群（必须是群主或管理员）
2. 点群右上角 **···** → **群机器人** → **添加**
3. 起个名字（比如"萨赫勒简报"），点 **添加**
4. 复制 **webhook 地址**（长得像 `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx`）
5. 填到 GitHub Secret `WECOM_WEBHOOK_URL`

---

## 渠道 ④ 钉钉群机器人

| 变量名 | 值（缺一不可） |
|---|---|
| `DINGTALK_WEBHOOK_URL` | 群的 webhook URL |
| `DINGTALK_SECRET` | （**可选**）如果开启了"加签验证"，需要填密钥 |

**如何拿 webhook：**

1. 打开钉钉 → 群聊天 → 右上角 **设置** → **智能群助手**
2. 点 **添加机器人** → **自定义**
3. 安全设置选择 **自定义关键词**（输入：`简报`、`西非`、`萨赫勒` 任意一个）
   > 或者选"加签"，把密钥填到 `DINGTALK_SECRET`
4. 点 **完成**，复制 webhook URL

---

## 渠道 ⑤ 飞书机器人

| 变量名 | 值 |
|---|---|
| `FEISHU_WEBHOOK_URL` | 飞书群机器人的 webhook URL |

**如何拿：**

1. 飞书 → 进群 → 右上角 **设置** → **群机器人** → **添加机器人** → **自定义机器人**
2. 起名字，点 **添加**，复制 webhook

---

## 渠道 ⑥ Telegram Bot

| 变量名 | 值 |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token（数字:字母） |
| `TELEGRAM_CHAT_ID` | 你的 chat ID（数字） |

**如何拿：**

1. 在 Telegram 里给 [@BotFather](https://t.me/BotFather) 发 `/newbot`
2. 给 bot 起个名字，会得到 **token**（长得像 `123456:ABC-DEF...`）
3. 在 Telegram 里给机器人发任意一句话
4. 浏览器访问 `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. JSON 里 `chat.id` 就是你的 **chat_id**
6. 把 token 和 chat_id 分别填到 Secrets

---

## 渠道 ⑦ Bark（iPhone 推送，免费 App）

| 变量名 | 值 |
|---|---|
| `BARK_URL` | 你的 Bark 服务器 URL（一般是 `https://api.day.app/你的KEY/`） |

**如何拿：**

1. iPhone 用国区/外区 App Store 搜"Bark"下载
2. 打开 App，App 里会显示你的 **服务器 URL** 和 KEY
3. 完整 URL 就是 `BARK_URL`
4. App 里可以单独配这个 channel 的开关、声音

---

## 渠道 ⑧ Discord Webhook

| 变量名 | 值 |
|---|---|
| `DISCORD_WEBHOOK_URL` | 服务器 webhook URL |

**如何拿：**

1. Discord 服务器 → 频道 → 右上角 **编辑频道** → **集成 / Webhooks**
2. 点 **新建 Webhook**，名字改一下，选你要的频道
3. 复制 **Webhook URL**

---

## 渠道 ⑨ Email（任意邮箱）

支持所有 SMTP 邮箱，包括 QQ / 163 / Gmail（发件）。

| 变量名 | 值 |
|---|---|
| `SMTP_HOST` | SMTP 服务器地址 |
| `SMTP_PORT` | 端口（QQ/163 SSL 用 465） |
| `SMTP_USER` | 发件邮箱地址 |
| `SMTP_PASSWORD` | 邮箱**授权码**（不是登录密码） |
| `EMAIL_FROM` | （可选）显示的发件人邮箱，默认 = SMTP_USER |
| `EMAIL_TO` | 收件人邮箱（自己） |

### QQ 邮箱

1. 登录 https://mail.qq.com/ → 顶部 **设置** → **账户** → 找到 **"SMTP 服务"**
2. 开启 SMTP，移动端扫码发送短信获取 **授权码**
3. 复制授权码 → 填到 `SMTP_PASSWORD`

| 变量 | 值 |
|---|---|
| `SMTP_HOST` | `smtp.qq.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | 你的 QQ 邮箱（如 `123456@qq.com`） |
| `SMTP_PASSWORD` | 上面拿到的授权码 |

### 163 邮箱

| 变量 | 值 |
|---|---|
| `SMTP_HOST` | `smtp.163.com` |
| `SMTP_PORT` | `465` |

操作同 QQ，开 SMTP + 授权码。

### Gmail（需要"应用专用密码"）

1. 登录 https://myaccount.google.com/security → 开启 **两步验证**
2. 搜索 **"应用专用密码"** → 生成一个名字叫"新闻简报"的密码
3. 把生成出来的 16 位密码填到 `SMTP_PASSWORD`

| 变量 | 值 |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `465` |

---

## 排查：推送失败了怎么办？

1. **看 Actions 日志**：
   https://github.com/samuelwhitaker96/news/actions
   点具体的运行记录，看红色文字里写了什么。

2. **最常见错误：**
   - **403 / 鉴权失败** → Secret 拼错了（多空格），或者重新生成密钥再粘一次
   - **限流** → Server酱免费版一天 5 条，今天可能用完了
   - **关键词拦截**（钉钉）→ 你设的关键词没包含"简报""西非"等
   - **SMTP 535** → 用的"登录密码"而不是"授权码"

3. **不要把密钥 commit 到代码**：所有密钥只能在 Secrets 里加，**绝不能写到任何代码文件里**。

---

## 测试推送

填好 Secret 后立刻想验证？两种方法：

**方法 A：手动触发 workflow**

进入 https://github.com/samuelwhitaker96/news/actions

→ 选 "Daily News Briefing" → "Run workflow" → 绿色按钮

→ 1-3 分钟后看日志底部有没有 `✅ X 个渠道推送成功`

**方法 B：本地直接跑**

```bash
# 在项目目录里
export SERVERCHAN_KEY="SCTxxxxx..."          # 改成你的
python scripts/push.py
```

Windows PowerShell：

```powershell
$env:SERVERCHAN_KEY = "SCTxxxxx..."
python scripts/push.py
```

跑完看终端输出，会显示每个渠道是 "OK" 还是 "skip"（跳过）还是 "ERR"。

---

## 推送格式

每个渠道看到的内容大致是这样：

```
📰 西非萨赫勒新闻简报 · 2026-08-07

## 国际媒体

### 🔥🔥🔥 [翻译后的标题]
[1-2 句中文摘要]
> 原文：[原文链接]

### 🔥🔥 [翻译后的标题]
...

——————
完整简报：https://samuelwhitaker96.github.io/news/
```

由于微信/钉钉等都有字数限制，超过会自动截断，但网站里是完整版。
