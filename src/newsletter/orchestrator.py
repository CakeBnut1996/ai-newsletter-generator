from __future__ import annotations

from pathlib import Path

from .config import load_newsletter_config
from .llm import GeminiNewsletterWriter
from .models import ArticleCandidate, NewsletterConfig, NewsletterPackage
from .news_service import fetch_article, read_rss_feed, search_google_news
from .render import build_html_document


class NewsletterOrchestrator:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

    def generate_from_skill(self, skill_path: str | Path) -> NewsletterPackage:
        config = load_newsletter_config(skill_path)
        return self.generate(config)

    def generate(self, config: NewsletterConfig) -> NewsletterPackage:
        articles = self._collect_articles(config)
        if not articles:
            raise RuntimeError("No articles were collected for the configured topic")

        writer = GeminiNewsletterWriter(model=config.llm_model)
        markdown = writer.write_newsletter(config, articles)
        title = self._extract_title(markdown)
        html = build_html_document(title=title, markdown_content=markdown)
        return NewsletterPackage(markdown=markdown, html=html, title=title)

    def _collect_articles(self, config: NewsletterConfig) -> list[ArticleCandidate]:
        candidates: list[dict] = []

        if config.sources:
            for feed_url in config.sources:
                candidates.extend(
                    read_rss_feed(
                        feed_url=feed_url,
                        max_results=config.max_articles,
                    )
                )
        else:
            candidates.extend(
                search_google_news(
                    topic=config.topic,
                    max_results=config.max_articles * 2,
                    language=config.language,
                )
            )

        unique_articles = self._dedupe_candidates(candidates)
        selected_articles = unique_articles[: config.max_articles]

        enriched_articles: list[ArticleCandidate] = []
        for item in selected_articles:
            article_payload = fetch_article(item["url"])
            enriched_articles.append(
                ArticleCandidate(
                    title=item["title"],
                    url=item["url"],
                    source=item.get("source", "Unknown source"),
                    published=item.get("published", "Unknown date"),
                    summary=item.get("summary", ""),
                    content=article_payload.get("content", ""),
                )
            )

        return enriched_articles

    def _dedupe_candidates(self, candidates: list[dict]) -> list[dict]:
        seen: set[str] = set()
        deduped: list[dict] = []
        for candidate in candidates:
            key = candidate.get("url") or candidate.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(candidate)
        return deduped

    def _extract_title(self, markdown: str) -> str:
        for line in markdown.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped.removeprefix("# ").strip()
        return "Newsletter"
