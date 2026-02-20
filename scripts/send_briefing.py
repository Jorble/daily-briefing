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
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "limit": 15},
        {"name": "极客公园", "url": "https://www.geekpark.net/feed", "limit": 8},
        {"name": "36氪", "url": "https://36kr.com/feed/", "limit": 8},
        {"name": "InfoQ", "url": "https://www.infoq.com/feed/", "limit": 8},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "limit": 12},
    ],
    "投资/金融": [
        {"name": "华尔街见闻", "url": "https://wallstreetcn.com/rss", "limit": 8},
        {"name": "财新网", "url": "http://www.caixin.com/atom.xml", "limit": 8},
        {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "limit": 8},
    ],
    "AI/科技前沿": [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "limit": 5},
        {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml", "limit": 5},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "limit": 8},
    ],
}

# 重要关键词 - 包含这些词的资讯会被优先保留
IMPORTANT_KEYWORDS = [
    "AI", "人工智能", "GPT", "Claude", "Claude", "OpenAI", "Anthropic", "Google", "微软", "Apple", "特斯拉",
    "融资", "上市", "收购", "发布", "推出", "突破", "重大", "最新",
    "亿美元", "亿人民币", "融资", "投资",
    "发布", "推出", "新品", "产品",
    "研究", "论文", "Science", "Nature", "arXiv", "大模型", "LLM"
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


def calculate_importance_score(title, translated_title):
    """计算重要性评分"""
    score = 0
    title_lower = title.lower()
    trans_lower = translated_title.lower() if translated_title else ""
    
    # 检查重要关键词加分
    for keyword in IMPORTANT_KEYWORDS:
        if keyword.lower() in title_lower or keyword.lower() in trans_lower:
            score += 10
    
    # 标题长度加分
    score += len(title) / 10
    
    return score


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
            
            # 计算重要性评分
            score = calculate_importance_score(title, translated_title)
            
            # 检查是否需要过滤
            title_lower = title.lower()
            should_filter = any(k.lower() in title_lower for k in FILTER_KEYWORDS)
            
            if not should_filter:
                entries.append({
                    "title": title,
                    "translated_title": translated_title,
                    "link": link,
                    "score": score,
                    "source": source["name"]
                })
        
        return entries
    except Exception as e:
        return []


def generate_summary(all_entries):
    """生成简单概要"""
    date_str = datetime.now().strftime("%m月%d日")
    ai_count = sum(1 for e in all_entries if any(k in e['translated_title'] or k in e['title'] for k in ['AI', '人工智能', 'GPT', 'Claude', '大模型']))
    tech_count = len(all_entries) - ai_count
    
    if ai_count > 0:
        return f"📌 {date_str}简报：{ai_count}条AI资讯，{tech_count}条其他科技要闻"
    else:
        return f"📌 {date_str}简报：今日{len(all_entries)}条重要资讯精选"


def generate_briefing():
    """生成每日简报"""
    # 收集所有资讯
    all_entries = []
    for category, sources in RSS_SOURCES.items():
        for source in sources:
            entries = parse_rss(source)
            all_entries.extend(entries)
    
    # 按重要性排序，取前20条
    all_entries.sort(key=lambda x: x["score"], reverse=True)
    top_entries = all_entries[:20]
    
    date_str = datetime.now().strftime("%Y年%m月%d日")
    briefing = f"📰 每日简报 - {date_str}\n\n"
    
    # 添加概要
    summary = generate_summary(top_entries)
    briefing += f"{summary}\n\n"
    
    # 按重要性展示
    briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    briefing += f"🔥 今日要闻 TOP 20\n"
    briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, entry in enumerate(top_entries, 1):
        display_title = entry["translated_title"] if entry["translated_title"] else entry["title"]
        briefing += f"{i:02d}. {display_title}\n"
        briefing += f"    {entry['link']}\n\n"
    
    briefing += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    return briefing


def send_telegram(message):
    """发送到Telegram"""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Missing Telegram credentials")
        return False

    MAX_LENGTH = 4000
    messages = [message[i : i + MAX_LENGTH] for i in range(0, len(message), MAX_LENGTH)]

    for msg in messages:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": msg}
        requests.post(url, json=data)

    return True


if __name__ == "__main__":
    briefing = generate_briefing()
    print(briefing)
    send_telegram(briefing)
