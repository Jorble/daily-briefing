#!/usr/bin/env python3
"""
市场哨兵 - 金融、AI、政治、军事领域每日监控
每天收集信息，总结最重要的6点，只包含全球性影响的重要事件
"""

import os
import feedparser
import html
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

# 扩展到四个领域的RSS源（专注全球性影响）
RSS_SOURCES = {
    "金融资讯": [
        {"name": "华尔街见闻", "url": "https://wallstreetcn.com/rss", "limit": 10},
        {"name": "财新网", "url": "http://www.caixin.com/atom.xml", "limit": 8},
        {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "limit": 8},
        {"name": "Reuters Business", "url": "https://feeds.reuters.com/reuters/businessNews", "limit": 8},
        {"name": "Financial Times", "url": "https://www.ft.com/?format=rss", "limit": 6},
    ],
    "AI/科技前沿": [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "limit": 5},
        {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml", "limit": 5},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "limit": 6},
        {"name": "Wired Tech", "url": "https://www.wired.com/feed/category/tech/latest/rss", "limit": 6},
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "limit": 8},
    ],
    "政治要闻": [
        {"name": "Reuters World", "url": "https://feeds.reuters.com/reuters/worldNews", "limit": 8},
        {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "limit": 6},
        {"name": "The Guardian World", "url": "https://www.theguardian.com/world/rss", "limit": 6},
        {"name": "Foreign Policy", "url": "https://foreignpolicy.com/feed/", "limit": 5},
        {"name": "Council on Foreign Relations", "url": "https://www.cfr.org/rss.xml", "limit": 4},
    ],
    "军事动态": [
        {"name": "Defense News", "url": "https://www.defensenews.com/arcio/rss/category/news/", "limit": 6},
        {"name": "Military Times", "url": "https://www.militarytimes.com/arcio/rss/category/news/", "limit": 5},
        {"name": "Janes Defence", "url": "https://www.janes.com/rss-feeds", "limit": 4},
        {"name": "US Department of Defense", "url": "https://www.defense.gov/News/Releases/RSS/", "limit": 5},
    ],
}

# 全球性影响的重要关键词
IMPORTANT_KEYWORDS = {
    "金融": [
        # 全球金融市场
        "美联储", "欧洲央行", "日本央行", "中国央行", "利率决议", "货币政策",
        "美元", "欧元", "人民币", "日元", "英镑", "汇率", "外汇储备",
        "通胀", "CPI", "PPI", "GDP", "经济衰退", "经济复苏",
        "股市", "纳斯达克", "标普500", "道琼斯", "上证指数", "恒生指数",
        "原油", "黄金", "大宗商品", "供应链", "贸易摩擦", "关税",
        # 重大企业事件
        "特斯拉", "英伟达", "谷歌", "微软", "苹果", "亚马逊", "Meta",
        "IPO", "并购", "收购", "融资", "估值", "财报", "营收", "利润",
        "破产", "重组", "制裁", "反垄断", "监管"
    ],
    "AI": [
        # AI技术突破
        "GPT", "Claude", "Gemini", "OpenAI", "Anthropic", "Google DeepMind",
        "大模型", "LLM", "多模态", "Agent", "RAG", "微调", "推理",
        "训练", "开源", "闭源", "API", "插件", "工具调用",
        # 重要应用和影响
        "自动驾驶", "医疗AI", "金融AI", "教育AI", "生成式AI",
        "AI安全", "AI伦理", "AI监管", "AI治理", "AI竞赛"
    ],
    "政治": [
        # 全球性政治事件
        "联合国", "G7", "G20", "北约", "欧盟", "东盟", "APEC",
        "中美关系", "美俄关系", "中俄关系", "中欧关系", "印太战略",
        "气候变化", "巴黎协定", "碳中和", "能源转型", "核不扩散",
        "选举", "政变", "宪法", "法律", "人权", "民主", "威权",
        "制裁", "禁运", "外交", "峰会", "谈判", "协议", "条约"
    ],
    "军事": [
        # 全球性军事事件
        "核武器", "核试验", "核威慑", "核扩散", "导弹", "洲际导弹",
        "航母", "战斗机", "无人机", "卫星", "网络战", "电子战",
        "军演", "部署", "基地", "联盟", "防御", "进攻", "冲突",
        "战争", "停火", "和平", "维和", "恐怖主义", "极端主义",
        "军费", "预算", "采购", "研发", "技术", "装备", "现代化"
    ]
}

# 过滤关键词（排除局部/小影响事件）
FILTER_KEYWORDS = [
    # 局部事件
    "地方", "市级", "县级", "乡镇", "社区", "村庄", "小镇",
    "local", "municipal", "county", "village", "town", "district",
    
    # 小规模事件
    "招聘", "求职", "job", "career", "hiring",
    "活动", "会议", "event", "webinar", "conference", "研讨会",
    "广告", "赞助", "sponsored", "promotion",
    "体育", "娱乐", "电影", "音乐", "游戏", "电竞",
    "健康", "医疗", "医药", "生物", "化学",
    "教育", "学校", "大学", "课程", "培训",
    
    # 低影响内容
    "日常", "生活", "美食", "旅游", "时尚", "美容",
    "天气", "交通", "房产", "汽车", "手机", "数码"
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

def calculate_importance_score(title, translated_title, category):
    """计算重要性评分（优先全球性影响）"""
    score = 0
    title_lower = title.lower()
    trans_lower = translated_title.lower() if translated_title else ""
    
    # 检查各领域重要关键词
    keywords = IMPORTANT_KEYWORDS.get(category, [])
    for keyword in keywords:
        if keyword.lower() in title_lower or keyword.lower() in trans_lower:
            # 全球性关键词给予更高分值
            if any(global_kw in keyword for global_kw in ["美联储", "联合国", "G7", "G20", "北约", "核武器", "核威慑", "全球"]):
                score += 25
            else:
                score += 15
    
    # 类别权重（政治和军事给更高权重，因为要求全球性影响）
    category_weights = {
        "金融资讯": 10,
        "AI/科技前沿": 8,
        "政治要闻": 12,
        "军事动态": 12
    }
    score += category_weights.get(category, 5)
    
    # 标题长度加分
    score += len(title) / 10
    
    return score

def parse_rss(source, category):
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
            score = calculate_importance_score(title, translated_title, category)
            
            # 检查是否需要过滤（排除局部/小影响事件）
            title_lower = title.lower()
            should_filter = any(k.lower() in title_lower for k in FILTER_KEYWORDS)
            
            if not should_filter and score > 10:  # 只保留评分较高的内容
                entries.append({
                    "title": title,
                    "translated_title": translated_title,
                    "link": link,
                    "score": score,
                    "category": category,
                    "source": source["name"]
                })
        
        return entries
    except Exception as e:
        print(f"Error parsing {source['name']}: {e}")
        return []

def generate_core_summary(top_entries):
    """生成不超过100字的核心内容简要"""
    # 统计各领域数量
    counts = {"金融资讯": 0, "AI/科技前沿": 0, "政治要闻": 0, "军事动态": 0}
    for entry in top_entries:
        counts[entry['category']] += 1
    
    # 提取关键主题
    keywords = []
    for entry in top_entries[:3]:  # 只看前3条最重要的
        title = entry['translated_title'] if entry['translated_title'] else entry['title']
        # 提取关键主题
        if any(kw in title for kw in ['美联储', '利率', '股市', '财报']):
            keywords.append('金融')
        elif any(kw in title for kw in ['GPT', 'AI', '大模型', 'OpenAI']):
            keywords.append('AI')
        elif any(kw in title for kw in ['联合国', 'G7', '选举', '外交']):
            keywords.append('政治')
        elif any(kw in title for kw in ['核武器', '军演', '冲突', '战争']):
            keywords.append('军事')
    
    keywords_str = '、'.join(list(set(keywords))) if keywords else '全球要闻'
    
    # 构建摘要
    summary_parts = []
    if counts["金融资讯"] > 0:
        summary_parts.append(f"{counts['金融资讯']}条金融")
    if counts["AI/科技前沿"] > 0:
        summary_parts.append(f"{counts['AI/科技前沿']}条AI")
    if counts["政治要闻"] > 0:
        summary_parts.append(f"{counts['政治要闻']}条政治")
    if counts["军事动态"] > 0:
        summary_parts.append(f"{counts['军事动态']}条军事")
    
    summary = f"今日{' + '.join(summary_parts)}要闻，重点关注：{keywords_str}"
    
    # 确保不超过100字
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary

def generate_market_sentinel():
    """生成市场哨兵日报"""
    # 收集所有四个领域的资讯
    all_entries = []
    for category, sources in RSS_SOURCES.items():
        for source in sources:
            entries = parse_rss(source, category)
            all_entries.extend(entries)
    
    # 按重要性排序，取前6条
    all_entries.sort(key=lambda x: x["score"], reverse=True)
    top_entries = all_entries[:6]
    
    if not top_entries:
        return "今日暂无全球性重要金融、AI、政治、军事资讯"
    
    date_str = datetime.now().strftime("%Y年%m月%d日")
    
    # 生成核心摘要（不超过100字）
    core_summary = generate_core_summary(top_entries)
    
    # 构建完整报告
    report = f"🚨 市场哨兵 - {date_str}\n\n"
    report += f"【核心摘要】\n{core_summary}\n\n"
    report += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"📊 今日重点（精选6条全球性影响事件）\n"
    report += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, entry in enumerate(top_entries, 1):
        display_title = entry["translated_title"] if entry["translated_title"] else entry["title"]
        category_emoji = {
            "金融资讯": "💰",
            "AI/科技前沿": "🤖", 
            "政治要闻": "🏛️",
            "军事动态": "⚔️"
        }.get(entry["category"], "📰")
        report += f"{i}. {category_emoji} {display_title}\n"
        report += f"   来源：{entry['source']}\n"
        report += f"   链接：{entry['link']}\n\n"
    
    report += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"数据来源：华尔街见闻、Reuters、BBC、OpenAI、Defense News等全球权威媒体\n"
    report += f"筛选标准：仅包含具有全球性影响的重要事件\n"
    report += f"生成时间：{datetime.now().strftime('%H:%M')}"
    
    return report

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
    report = generate_market_sentinel()
    print(report)
    send_telegram(report)