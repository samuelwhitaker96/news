"""简报自动推送：把当日简报发到多个渠道。

每个渠道独立读取对应的环境变量，没配就跳过，全部失败也不影响主流程。

支持的渠道（按"国内小白用户友好度"排序）：

  微信（推荐）
    SERVERCHAN_KEY              Server酱·Turbo 版的 SendKey（推荐）
                               文档：https://sct.ftqq.com/
                               注意：免费版每日 5 条上限。

  企业微信群机器人
    WECOM_WEBHOOK_URL           群机器人 webhook URL
                               文档：https://developer.work.weixin.qq.com/document/path/91770

  钉钉群机器人
    DINGTALK_WEBHOOK_URL        群机器人 webhook URL
    DINGTALK_SECRET             (可选) 加签密钥，开启加签时必填
                               文档：https://open.dingtalk.com/document/orgapp/robot-overview

  飞书群机器人
    FEISHU_WEBHOOK_URL          群机器人 webhook URL
                               文档：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot

  Discord
    DISCORD_WEBHOOK_URL         服务器 webhook URL

  Telegram
    TELEGRAM_BOT_TOKEN          bot token (xxx:yyy)
    TELEGRAM_CHAT_ID            你的 chat ID（群或个人）

  PushPlus（微信公众号聚合推送，无需企业认证）
    PUSHPLUS_TOKEN              在 pushplus.plus 注册的 token
                               文档：https://www.pushplus.plus/doc/

  Bark（iOS 推送通知）
    BARK_URL                    例如 https://api.day.app/yourkey
                               文档：https://bark.day.app/

  通用 SMTP 邮件
    SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASSWORD EMAIL_FROM EMAIL_TO
                               收件人 EMAIL_TO 默认 = SMTP_USER
"""
import base64
import hashlib
import hmac
import json
import os
import re
import smtplib
import time
import urllib.parse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
CONTENT_DIR = ROOT / "content"
SITE_DIR = ROOT / "site"


# ---------------------------------------------------------------------------
# 工具：生成推送内容
# ---------------------------------------------------------------------------

def load_today_briefing() -> tuple[str, str]:
    today = datetime.now().strftime("%Y-%m-%d")
    md_path = CONTENT_DIR / f"{today}.md"
    if not md_path.exists():
        return today, ""
    return today, md_path.read_text(encoding="utf-8")


def md_to_plain(md: str) -> str:
    """把 markdown 转成纯文本（用于推送）"""
    text = md
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1（\2）", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def md_to_html(md: str) -> str:
    """简单 markdown → HTML（邮件用）"""
    html = md
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  r'<a href="\2">\1</a>', html)
    html = re.sub(r"^>\s*(.+)$", r"<blockquote>\1</blockquote>",
                  html, flags=re.MULTILINE)
    html = re.sub(r"^---+\s*$", "<hr>", html, flags=re.MULTILINE)
    html = re.sub(r"\n\n", "</p><p>", html)
    html = f"<html><body><p>{html}</p></body></html>"
    return html


def make_summary(date: str, md: str) -> str:
    """生成简短的"推送摘要"（不含 markdown 装饰）"""
    plain = md_to_plain(md)
    site_url = "https://samuelwhitaker96.github.io/news/"  # 默认
    header = f"📰 西非萨赫勒新闻简报 · {date}\n"
    footer = f"\n——————\n完整简报：{site_url}"
    return (header + plain + footer).strip()


# ---------------------------------------------------------------------------
# 渠道 1：Server酱（微信推送，最推荐）
# ---------------------------------------------------------------------------

def push_serverchan(date: str, text: str) -> bool:
    """Server酱 → 微信（推荐）"""
    key = os.environ.get("SERVERCHAN_KEY", "").strip()
    if not key:
        print("  [skip] Server酱: SERVERCHAN_KEY 未设置")
        return False
    # 兼容新旧域名 + SendKey
    url_candidates = [
        f"https://sctapi.ftqq.com/{key}.send",
        f"https://sc.ftqq.com/{key}.send",
    ]
    short = text[:80] + "..." if len(text) > 80 else text
    for url in url_candidates:
        try:
            r = requests.post(url, data={
                "title": f"📰 西非萨赫勒简报 · {date}",
                "desp": text,
                "short": short,
            }, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if data.get("code") == 0:
                    print("  [OK] Server酱 → 微信 推送成功")
                    return True
                print(f"  [ERR] Server酱: {data.get('msg', data)[:160]}")
                continue
            print(f"  [ERR] Server酱: HTTP {r.status_code}")
        except Exception as e:
            print(f"  [ERR] Server酱: {e}")
    return False


# ---------------------------------------------------------------------------
# 渠道 2：企业微信群机器人
# ---------------------------------------------------------------------------

def push_wecom(date: str, text: str) -> bool:
    """企业微信群机器人（公司群里最稳定）"""
    url = os.environ.get("WECOM_WEBHOOK_URL", "").strip()
    if not url:
        print("  [skip] 企业微信: WECOM_WEBHOOK_URL 未设置")
        return False
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"## 📰 西非萨赫勒新闻简报 · {date}\n\n"
                       f"{text[:3500]}",
        },
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200 and r.json().get("errcode") == 0:
            print("  [OK] 企业微信 推送成功")
            return True
        print(f"  [ERR] 企业微信: {r.status_code} {r.text[:160]}")
        return False
    except Exception as e:
        print(f"  [ERR] 企业微信: {e}")
        return False


# ---------------------------------------------------------------------------
# 渠道 3：钉钉群机器人
# ---------------------------------------------------------------------------

def _dingtalk_sign(secret: str) -> tuple[str, str]:
    """计算钉钉加签"""
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def push_dingtalk(date: str, text: str) -> bool:
    url = os.environ.get("DINGTALK_WEBHOOK_URL", "").strip()
    if not url:
        print("  [skip] 钉钉: DINGTALK_WEBHOOK_URL 未设置")
        return False
    secret = os.environ.get("DINGTALK_SECRET", "").strip()
    if secret:
        ts, sign = _dingtalk_sign(secret)
        url = url + (f"&timestamp={ts}&sign={sign}"
                     if "?" in url else f"?timestamp={ts}&sign={sign}")
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": f"📰 西非萨赫勒简报 · {date}",
            "text": f"## 📰 西非萨赫勒新闻简报 · {date}\n\n{text[:3500]}",
        },
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200 and r.json().get("errcode") == 0:
            print("  [OK] 钉钉 推送成功")
            return True
        print(f"  [ERR] 钉钉: {r.status_code} {r.text[:160]}")
        return False
    except Exception as e:
        print(f"  [ERR] 钉钉: {e}")
        return False


# ---------------------------------------------------------------------------
# 渠道 4：飞书机器人
# ---------------------------------------------------------------------------

def push_feishu(date: str, text: str) -> bool:
    url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    if not url:
        print("  [skip] 飞书: FEISHU_WEBHOOK_URL 未设置")
        return False
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📰 西非萨赫勒简报 · {date}",
                },
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": text[:3500],
                },
            ],
        },
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200 and r.json().get("code") == 0:
            print("  [OK] 飞书 推送成功")
            return True
        print(f"  [ERR] 飞书: {r.status_code} {r.text[:160]}")
        return False
    except Exception as e:
        print(f"  [ERR] 飞书: {e}")
        return False


# ---------------------------------------------------------------------------
# 渠道 5：Discord
# ---------------------------------------------------------------------------

def push_discord(date: str, text: str) -> bool:
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        print("  [skip] Discord: DISCORD_WEBHOOK_URL 未设置")
        return False
    payload = {"content": f"📰 西非萨赫勒简报 · {date}\n\n{text[:1900]}"}
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code in (200, 204):
            print("  [OK] Discord 推送成功")
            return True
        print(f"  [ERR] Discord: HTTP {r.status_code}")
        return False
    except Exception as e:
        print(f"  [ERR] Discord: {e}")
        return False


# ---------------------------------------------------------------------------
# 渠道 6：Telegram
# ---------------------------------------------------------------------------

def push_telegram(date: str, text: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("  [skip] Telegram: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 未设置")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"📰 *西非萨赫勒简报 · {date}*\n\n{text[:3800]}",
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            print("  [OK] Telegram 推送成功")
            return True
        print(f"  [ERR] Telegram: HTTP {r.status_code}")
        return False
    except Exception as e:
        print(f"  [ERR] Telegram: {e}")
        return False


# ---------------------------------------------------------------------------
# 渠道 7：PushPlus（推到微信公众号）
# ---------------------------------------------------------------------------

def push_pushplus(date: str, text: str) -> bool:
    token = os.environ.get("PUSHPLUS_TOKEN", "").strip()
    if not token:
        print("  [skip] PushPlus: PUSHPLUS_TOKEN 未设置")
        return False
    url = "https://www.pushplus.plus/send"
    payload = {
        "token": token,
        "title": f"📰 西非萨赫勒简报 · {date}",
        "content": text,
        "template": "markdown",
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200 and r.json().get("code") == 200:
            print("  [OK] PushPlus 推送成功")
            return True
        print(f"  [ERR] PushPlus: {r.status_code} {r.text[:160]}")
        return False
    except Exception as e:
        print(f"  [ERR] PushPlus: {e}")
        return False


# ---------------------------------------------------------------------------
# 渠道 8：Bark（iOS）
# ---------------------------------------------------------------------------

def push_bark(date: str, text: str) -> bool:
    url = os.environ.get("BARK_URL", "").strip()
    if not url:
        print("  [skip] Bark: BARK_URL 未设置")
        return False
    # Bark 限制 body 在 ~4000 字符以内
    payload = {
        "title": f"📰 西非萨赫勒简报 · {date}",
        "body": text[:3500],
        "group": "news-briefing",
        "icon": "https://cdn-icons-png.flaticon.com/512/2965/2965878.png",
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            print("  [OK] Bark 推送成功")
            return True
        print(f"  [ERR] Bark: HTTP {r.status_code}")
        return False
    except Exception as e:
        print(f"  [ERR] Bark: {e}")
        return False


# ---------------------------------------------------------------------------
# 渠道 9：邮件
# ---------------------------------------------------------------------------

def push_email(date: str, md: str) -> bool:
    host = os.environ.get("SMTP_HOST", "").strip()
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    sender = os.environ.get("EMAIL_FROM", user).strip()
    receiver = os.environ.get("EMAIL_TO", "").strip()
    if not all([host, user, password, receiver]):
        print("  [skip] Email: SMTP_HOST/USER/PASSWORD/EMAIL_TO 未全部设置")
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 西非萨赫勒新闻简报 · {date}"
    msg["From"] = sender
    msg["To"] = receiver
    msg.attach(MIMEText(md_to_plain(md), "plain", "utf-8"))
    msg.attach(MIMEText(md_to_html(md), "html", "utf-8"))
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(user, password)
                smtp.send_message(msg)
        print(f"  [OK] Email 推送成功 → {receiver}")
        return True
    except Exception as e:
        print(f"  [ERR] Email: {e}")
        return False


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

CHANNELS = [
    ("Server酱 → 微信",     push_serverchan),
    ("企业微信群机器人",      push_wecom),
    ("钉钉群机器人",          push_dingtalk),
    ("飞书机器人",            push_feishu),
    ("PushPlus（微信）",      push_pushplus),
    ("Discord",              push_discord),
    ("Telegram",             push_telegram),
    ("Bark (iOS)",           push_bark),
    ("Email",                push_email),
]


def main():
    date, md = load_today_briefing()
    if not md:
        print(f"[ERR] 今天的简报不存在: content/{date}.md")
        print("请先跑 fetch_rss.py + summarize.py")
        return 1

    text = make_summary(date, md)
    print(f"推送 {date} 简报到各渠道...\n")
    print(f"  摘要长度：{len(text)} 字符\n")

    success = 0
    for name, fn in CHANNELS:
        print(f"[{name}]")
        try:
            if fn(date, text):
                success += 1
        except Exception as e:
            print(f"  [ERR] {name}: {e}")
        print()

    if success == 0:
        print("⚠️  所有渠道都跳过了。需要在 GitHub Secrets 里配置至少一个渠道。")
    else:
        print(f"✅ {success} 个渠道推送成功。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
