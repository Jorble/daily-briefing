# 每日简报

自动抓取 RSS 资讯并通过 Telegram 发送每日简报。

## 功能

- 每天自动运行（早上 8 点）
- 抓取 16 个 RSS 源
- 发送到 Telegram

## RSS 源

### 技术资讯
- Hacker News
- 极客公园
- 36氪
- 钛媒体
- InfoQ
- TechCrunch
- The Verge

### 投资/金融
- 华尔街见闻
- 财新网
- 经济观察报
- Bloomberg

### AI/科技前沿
- OpenAI Blog
- Anthropic Blog
- MIT Tech Review
- Wired Tech

## 设置步骤

### 1. 创建 Telegram Bot
1. 在 Telegram 搜索 @BotFather
2. 发送 `/newbot` 创建机器人
3. 获取 Bot Token

### 2. 获取 Chat ID
1. 在 Telegram 搜索 @userinfobot
2. 发送任意消息获取你的 Chat ID

### 3. 配置 GitHub Secrets
在 GitHub 仓库设置中添加以下 Secrets：
- `TELEGRAM_BOT_TOKEN`: 你的 Bot Token
- `TELEGRAM_CHAT_ID`: 你的 Chat ID

### 4. 启用 GitHub Actions
1. 推送代码到 GitHub 仓库
2. 前往 Actions 查看运行状态

## 本地测试

```bash
pip install feedparser requests
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python scripts/send_briefing.py
```

## 自定义

修改 `scripts/send_briefing.py` 中的 `RSS_SOURCES` 来自定义RSS源。
