from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class NewsletterConfig:
    name: str
    description: str
    audience: str
    tone: str
    llm_provider: str
    llm_model: str
    language: str
    max_articles: int
    open_in_browser: bool
    sources: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    output_item_label: str = "Training"
    output_fields: list[str] = field(default_factory=list)
    url_style: str = "wrapped_link"
    url_label: str = "Open source"
    editorial_brief: str = ""
    skill_path: Path | None = None
    topic: str = ""
    sector_focus: str = ""


@dataclass(slots=True)
class ArticleCandidate:
    title: str
    url: str
    source: str
    published: str
    summary: str = ""
    content: str = ""


@dataclass(slots=True)
class NewsletterPackage:
    markdown: str
    html: str
    title: str
    markdown_path: Path | None = None
    html_path: Path | None = None
