# AGENTS.md - Daily Briefing Project

Guidelines for AI agents working in this repository.

## Project Overview

Daily Briefing is a Python project that automatically fetches RSS feeds and sends daily news digests via Telegram. It runs on GitHub Actions daily at 8:00 AM.

## Build & Run Commands

### Local Development

```bash
# Install dependencies
pip install feedparser requests

# Run the briefing script
python scripts/send_briefing.py

# Or test the news fetcher
python fetch_news.py
```

### Environment Variables

Required for Telegram integration:
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

### Testing

```bash
# Run with test credentials
TELEGRAM_BOT_TOKEN="test_token" TELEGRAM_CHAT_ID="test_id" python scripts/send_briefing.py

# Test just the RSS fetching
python fetch_news.py
```

## Code Style Guidelines

### General Principles

- Keep functions small and focused (under 50 lines when possible)
- Use descriptive variable and function names
- Add docstrings to all public functions
- Handle exceptions gracefully with meaningful error messages

### Python Style

- **Formatting**: Use 4 spaces for indentation (no tabs)
- **Line length**: Maximum 100 characters
- **Imports**: Group in order: stdlib, third-party, local
  ```python
  import os
  import feedparser
  import requests
  from datetime import datetime
  ```
- **Naming**:
  - Functions/variables: `snake_case` (e.g., `parse_rss`, `bot_token`)
  - Classes: `PascalCase` (e.g., `RSSParser`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_LENGTH`)
- **Strings**: Use f-strings for formatting, double quotes for simple strings
- **Type hints**: Not required but appreciated for complex functions

### Error Handling

- Catch specific exceptions rather than using bare `except`
- Return error information in structured form (dict with "error" key)
- Log errors but don't expose sensitive details

```python
# Good
try:
    feed = feedparser.parse(source["url"])
except Exception as e:
    return {"name": source["name"], "entries": [], "error": str(e)}

# Avoid
try:
    feed = feedparser.parse(source["url"])
except:
    print("Error")
```

### Git Conventions

- Commit messages: Use clear, present-tense descriptions
- Branch naming: `feature/description` or `fix/description`
- No need to run lint/tests before commit (simple project)

## Project Structure

```
daily-briefing/
├── fetch_news.py        # RSS fetcher (standalone)
├── scripts/
│   └── send_briefing.py # Main script (fetches + sends to Telegram)
├── .github/
│   └── workflows/
│       └── daily-briefing.yml  # GitHub Actions workflow
└── README.md
```

## Key Files

| File | Purpose |
|------|---------|
| `scripts/send_briefing.py` | Main entry point |
| `fetch_news.py` | RSS parsing logic |
| `RSS_SOURCES` dict | Configuration of RSS feeds |

## Modifying RSS Sources

Edit the `RSS_SOURCES` dictionary in either file to add/remove feeds:

```python
RSS_SOURCES = {
    "Category Name": [
        {"name": "Feed Name", "url": "https://example.com/feed", "limit": 5},
    ],
}
```

## Telegram Integration

- Bot creation: @BotFather on Telegram
- Get Chat ID: @userinfobot on Telegram
- Store credentials in GitHub Secrets for CI/CD
