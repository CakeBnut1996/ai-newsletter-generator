from __future__ import annotations

from urllib.parse import quote_plus

import feedparser
import requests
import trafilatura


USER_AGENT = "ai-newsletter-generator/1.0"


def search_google_news(topic: str, max_results: int = 8, language: str = "en-US") -> list[dict]:
    language_code = language.split("-")[0]
    query = quote_plus(topic)
    feed_url = (
        f"https://news.google.com/rss/search?q={query}&hl={language}&gl=US&ceid=US:{language_code}"
    )
    parsed_feed = feedparser.parse(feed_url)
    return _normalize_feed_entries(parsed_feed, max_results)


def read_rss_feed(feed_url: str, max_results: int = 8) -> list[dict]:
    parsed_feed = feedparser.parse(feed_url)
    return _normalize_feed_entries(parsed_feed, max_results)


def fetch_article(url: str, max_chars: int = 6000) -> dict:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()

    extracted_text = trafilatura.extract(response.text, include_comments=False, include_tables=False)
    content = (extracted_text or response.text)[:max_chars]
    return {"url": url, "content": content}


def _normalize_feed_entries(parsed_feed: feedparser.FeedParserDict, max_results: int) -> list[dict]:
    items: list[dict] = []
    for entry in parsed_feed.entries[:max_results]:
        source = "Unknown source"
        if getattr(entry, "source", None) and getattr(entry.source, "title", None):
            source = entry.source.title
        elif getattr(parsed_feed.feed, "title", None):
            source = parsed_feed.feed.title

        items.append(
            {
                "title": getattr(entry, "title", "Untitled story"),
                "url": getattr(entry, "link", ""),
                "source": source,
                "published": getattr(entry, "published", "Unknown date"),
                "summary": getattr(entry, "summary", ""),
            }
        )
    return items