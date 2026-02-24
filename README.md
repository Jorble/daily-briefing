# 市场哨兵

金融、AI、政治、军事领域每日监控，每天收集全球性影响的重要事件，总结最重要的6点。

## 功能

- 每天自动运行（早上8点）
- 专注四个核心领域：金融、AI、政治、军事
- **仅包含全球性影响的重要事件**（排除局部/小影响事件）
- 智能筛选最重要的6条信息
- 提供不超过100字的核心内容简要
- 发送到Telegram

## 监控范围

### 金融资讯
- 华尔街见闻、财新网、Bloomberg、Reuters、Financial Times

### AI/科技前沿  
- OpenAI Blog、Anthropic Blog、MIT Tech Review、Wired Tech、Hacker News

### 政治要闻
- Reuters World、BBC World、The Guardian、Foreign Policy、Council on Foreign Relations

### 军事动态
- Defense News、Military Times、Janes Defence、US Department of Defense

## 筛选标准

### ✅ 包含的内容
- **全球性影响**：G7/G20/联合国决议、美联储政策、重大国际冲突
- **重大技术突破**：GPT-5发布、AI安全框架、重要开源项目
- **金融市场重大事件**：主要股指大幅波动、重要企业财报、重大并购
- **国际政治事件**：重要选举、外交关系变化、国际协议签署

### ❌ 排除的内容  
- **局部事件**：地方新闻、市级/县级事件
- **小规模事件**：招聘、会议、日常活动
- **低影响内容**：体育、娱乐、生活类新闻
- **非全球性影响**：仅影响单个国家或地区的事件

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
pip install feedparser requests deep-translator
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python scripts/market_sentinel.py
```

## 自定义

修改 `scripts/market_sentinel.py` 中的 `RSS_SOURCES`、`IMPORTANT_KEYWORDS` 或 `FILTER_KEYWORDS` 来调整监控范围和筛选标准。