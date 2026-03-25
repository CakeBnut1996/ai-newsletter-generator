from __future__ import annotations

from pathlib import Path
import re

import yaml

from .models import NewsletterConfig


FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def load_newsletter_config(skill_path: str | Path) -> NewsletterConfig:
    path = Path(skill_path).expanduser().resolve()
    raw_text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(raw_text)
    if not match:
        raise ValueError(f"Skill file is missing YAML frontmatter: {path}")

    frontmatter_text, body = match.groups()
    metadata = yaml.safe_load(frontmatter_text) or {}
    skill_metadata = metadata.get("metadata", {}) if isinstance(metadata.get("metadata", {}), dict) else {}

    def get_value(key: str, default=None):
        if key in skill_metadata:
            return skill_metadata.get(key)
        return metadata.get(key, default)

    def as_str(value, default: str) -> str:
        if value is None:
            return default
        return str(value)

    def as_int(value, default: int) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def as_bool(value, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "on"}
        return bool(value)

    def as_list_str(value, default: list[str]) -> list[str]:
        if value is None:
            return default
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        return default

    topic = get_value("topic") or get_value("sector_focus", "")
    if not topic:
        raise ValueError(f"Skill file must have either 'topic' or 'sector_focus' field: {path}")

    return NewsletterConfig(
        name=metadata.get("name", path.stem),
        description=metadata.get("description", ""),
        topic=topic,
        audience=as_str(get_value("audience", "General audience"), "General audience"),
        tone=as_str(get_value("tone", "Clear and practical"), "Clear and practical"),
        llm_provider=as_str(get_value("llm_provider", "gemini"), "gemini"),
        llm_model=as_str(get_value("llm_model", "gemini-2.5-flash"), "gemini-2.5-flash"),
        language=as_str(get_value("language", "en-US"), "en-US"),
        max_articles=as_int(get_value("max_articles", 6), 6),
        open_in_browser=as_bool(get_value("open_in_browser", True), True),
        sources=as_list_str(get_value("sources", []), []),
        sections=as_list_str(get_value("sections", []), []),
        output_item_label=as_str(get_value("output_item_label", "Training"), "Training"),
        output_fields=as_list_str(
            get_value(
                "output_fields",
                ["Date", "Provider", "Audience", "Why it matters", "URL"],
            ),
            ["Date", "Provider", "Audience", "Why it matters", "URL"],
        ),
        url_style=as_str(get_value("url_style", "wrapped_link"), "wrapped_link"),
        url_label=as_str(get_value("url_label", "Open source"), "Open source"),
        editorial_brief=body.strip(),
        skill_path=path,
        sector_focus=as_str(get_value("sector_focus", ""), ""),
    )
