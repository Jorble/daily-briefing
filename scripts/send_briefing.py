#!/usr/bin/env python3
"""
每日简报生成并发送到Telegram
"""

import os
import feedparser
import html
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

RSS_SOURCES = {
    "技术资讯": [
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "limit": 10},
        {"name": "极客公园", "url": "https://www.geekpark.net/feed", "limit": 5},
        {"name": "36氪", "url": "https://36kr.com/feed/", "limit": 5},
        {"name": "InfoQ", "url": "https://www.infoq.com/feed/", "limit": 5},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "limit": 8},
    ],
    "投资/金融": [
        {"name": "华尔街见闻", "url": "https://wallstreetcn.com/rss", "limit": 5},
        {"name": "财新网", "url": "http://www.caixin.com/atom.xml", "limit": 5},
        {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "limit": 5},
    ],
    "AI/科技前沿": [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "limit": 3},
        {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml", "limit": 3},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "limit": 5},
    ],
}

# 重要关键词 - 包含这些词的资讯会被优先保留
IMPORTANT_KEYWORDS = [
    "AI", "人工智能", "GPT", "Claude", "OpenAI", "Anthropic", "Google", "微软", "Apple", "特斯拉",
    "融资", "上市", "收购", "发布", "推出", "突破", "重大", "最新",
    "亿美元", "亿人民币", "融资", "投资",
    "发布", "推出", "新品", "产品",
    "研究", "论文", "Science", "Nature", "arXiv"
]

# 过滤关键词 - 包含这些词的资讯会被过滤
FILTER_KEYWORDS = [
    "job", "jobs", "招聘", "求职", "hiring", "career",
    "event", "events", "活动", "会议", "webinar",
    "sponsored", "赞助", "广告", "promotion"
]


def is_chinese(text):
    """判断文本是否为中文"""
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def translate_text(text):
    """翻译文本为中文"""
    if not text or is_chinese(text):
        return text
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except:
        return text


def is_important(title):
    """判断资讯是否重要"""
    title_lower = title.lower()
    
    # 检查是否包含过滤关键词
    for keyword in FILTER_KEYWORDS:
        if keyword.lower() in title_lower:
            return False
    
    # 检查是否包含重要关键词
    for keyword in IMPORTANT_KEYWORDS:
        if keyword.lower() in title_lower:
            return True
    
    # 标题较长的可能更重要
    return len(title) > 20


def parse_rss(source):
    """解析单个RSS源"""
    try:
        feed = feedparser.parse(source["url"])
        entries = []
        for entry in feed.entries[:source["limit"]]:
            title = html.unescape(entry.get("title", "无标题"))
            link = entry.get("link", "")
            
            # 翻译标题
            translated_title = translate_text(title)
            
            entries.append({
                "title": title,
                "translated_title": translated_title,
                "link": link,
                "important": is_important(title) or is_important(translated_title)
            })
        
        # 优先展示重要资讯
        entries.sort(key=lambda x: (not x["important"], len(x["title"])), reverse=True)
        
        return {"name": source["name"], "entries": entries, "error": None}
    except Exception as e:
        return {"name": source["name"], "entries": [], "error": str(e)}


def generate_briefing():
    """生成每日简报"""
    date_str = datetime.now().strftime("%Y年%m月%d日")
    briefing = f"📰 每日简报 - {date_str}\n\n"
    total_items = 0
    important_items = 0

    for category, sources in RSS_SOURCES.items():
        briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        briefing += f"📂 {category}\n"
        briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for source in sources:
            result = parse_rss(source)
            if result["error"]:
                continue
            if not result["entries"]:
                continue
            
            # 只保留重要的或前3条
            filtered_entries = []
            for entry in result["entries"]:
                if entry["important"] or len(filtered_entries) < 3:
                    filtered_entries.append(entry)
            
            if not filtered_entries:
                continue
                
            briefing += f"🔹 {result['name']}\n"
            for entry in filtered_entries:
                prefix = "🔥" if entry["important"] else "•"
                display_title = entry["translated_title"] if entry["translated_title"] else entry["title"]
                briefing += f"  {prefix} {display_title}\n"
                briefing += f"    {entry['link']}\n"
            briefing += "\n"
            total_items += len(filtered_entries)
            important_items += sum(1 for e in filtered_entries if e["important"])

    briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    briefing += f"共收集 {total_items} 条资讯"
    if important_items > 0:
        briefing += f"（含 {important_items} 条重要资讯）"
    return briefing


def send_telegram(message):
    """发送到Telegram"""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Missing Telegram credentials")
        print(f"Bot token: {'***' if bot_token else 'NOT SET'}")
        print(f"Chat ID: {'***' if chat_id else 'NOT SET'}")
        return False

    print(f"Sending to chat ID: {chat_id}")
    MAX_LENGTH = 4000
    messages = [message[i : i + MAX_LENGTH] for i in range(0, len(message), MAX_LENGTH)]

    for i, msg in enumerate(messages):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": msg}
        response = requests.post(url, json=data)
        print(f"Message {i+1} - Status: {response.status_code}")

    return True


if __name__ == "__main__":
    briefing = generate_briefing()
    print(briefing)
    print("\n" + "=" * 40 + "\n")
    send_telegram(briefing)
