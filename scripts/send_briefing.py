#!/usr/bin/env python3
"""
每日简报生成并发送到Telegram
"""

import os
import feedparser
import html
import requests
from datetime import datetime

RSS_SOURCES = {
    "技术资讯": [
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "limit": 5},
        {"name": "极客公园", "url": "https://www.geekpark.net/feed", "limit": 5},
        {"name": "36氪", "url": "https://36kr.com/feed/", "limit": 5},
        {"name": "钛媒体", "url": "https://www.tmtpost.com/feed", "limit": 5},
        {"name": "InfoQ", "url": "https://www.infoq.com/feed/", "limit": 5},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "limit": 5},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "limit": 5},
    ],
    "投资/金融": [
        {"name": "华尔街见闻", "url": "https://wallstreetcn.com/rss", "limit": 5},
        {"name": "财新网", "url": "http://www.caixin.com/atom.xml", "limit": 5},
        {"name": "经济观察报", "url": "https://www.eeo.com.cn/feed/", "limit": 5},
        {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "limit": 5},
    ],
    "AI/科技前沿": [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "limit": 5},
        {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml", "limit": 5},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "limit": 5},
        {"name": "Wired Tech", "url": "https://www.wired.com/feed/category/tech/latest/rss", "limit": 5},
    ],
}


def parse_rss(source):
    """解析单个RSS源"""
    try:
        feed = feedparser.parse(source["url"])
        entries = []
        for entry in feed.entries[:source["limit"]]:
            title = html.unescape(entry.get("title", "无标题"))
            link = entry.get("link", "")
            entries.append({"title": title, "link": link})
        return {"name": source["name"], "entries": entries, "error": None}
    except Exception as e:
        return {"name": source["name"], "entries": [], "error": str(e)}


def generate_briefing():
    """生成每日简报"""
    date_str = datetime.now().strftime("%Y年%m月%d日")
    briefing = f"📰 每日简报 - {date_str}\n\n"
    total_items = 0

    for category, sources in RSS_SOURCES.items():
        briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        briefing += f"📂 {category}\n"
        briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for source in sources:
            result = parse_rss(source)
            if result["error"]:
                briefing += f"❌ {result['name']}: {result['error']}\n\n"
                continue
            if not result["entries"]:
                continue
            briefing += f"🔹 {result['name']}\n"
            for entry in result["entries"]:
                briefing += f"  • {entry['title']}\n"
                briefing += f"    {entry['link']}\n"
            briefing += "\n"
            total_items += len(result["entries"])

    briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    briefing += f"共收集 {total_items} 条资讯"
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
        print(f"Response: {response.text}")

    return True


if __name__ == "__main__":
    briefing = generate_briefing()
    print(briefing)
    print("\n" + "=" * 40 + "\n")
    send_telegram(briefing)
