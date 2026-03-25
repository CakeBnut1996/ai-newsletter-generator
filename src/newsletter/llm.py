from __future__ import annotations

import json
import os
import re

from google import genai

from .models import ArticleCandidate, NewsletterConfig


class GeminiNewsletterWriter:
    def __init__(self, model: str, api_key: str | None = None):
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=resolved_api_key)
        self.model = model

    def write_newsletter(self, config: NewsletterConfig, articles: list[ArticleCandidate]) -> str:
        source_catalog: list[dict[str, str]] = []
        source_blocks: list[str] = []
        for index, article in enumerate(articles, start=1):
            source_id = f"S{index}"
            source_catalog.append(
                {
                    "source_id": source_id,
                    "title": article.title,
                    "source": article.source,
                    "published": article.published,
                    "url": article.url,
                    "summary": article.summary,
                }
            )
            source_blocks.append(
                "\n".join(
                    [
                        f"Source ID: {source_id}",
                        f"Title: {article.title}",
                        f"Provider/Publisher: {article.source}",
                        f"Published: {article.published}",
                        f"URL: {article.url}",
                        f"Summary: {article.summary}",
                        f"Extract: {article.content[:2000]}",
                    ]
                )
            )

        section_title = config.sections[0] if config.sections else "Training Updates"
        prompt = f"""
You are writing a recurring newsletter from the provided sources.

Newsletter topic: {config.topic}
Audience: {config.audience}
Tone: {config.tone}
Section heading to use: {section_title}

Editorial brief:
{config.editorial_brief}

Output rules:
- Respond with valid JSON only (no markdown, no code fences).
- Use this schema exactly:
  {{
    "title": "string",
    "opening_summary": "string",
    "closing_takeaway": "string",
    "items": [
      {{
        "training": "string",
        "date": "YYYY-MM-DD or original date text",
        "provider": "string",
        "audience": "operators|apprenticeship|college|two-year college|trade school|K-12",
        "why_it_matters": "string",
        "source_id": "S#"
      }}
    ]
  }}
- The source_id must be one of the provided source IDs.
- Do not invent URLs. URLs will be attached from source_id only.
- The output markdown will use this item label: {config.output_item_label}
- The output markdown will use these sub-bullet fields in this order: {', '.join(config.output_fields)}

Source material:
{"\n\n".join(source_blocks)}
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        response_text = getattr(response, "text", "")
        if not response_text:
            raise RuntimeError("Gemini returned an empty newsletter")

        payload = self._parse_json_response(response_text)
        return self._render_markdown(config, payload, source_catalog)

    def _parse_json_response(self, response_text: str) -> dict:
        cleaned = response_text.strip()
        fence_match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
        if fence_match:
            cleaned = fence_match.group(1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise RuntimeError("Gemini returned malformed JSON for newsletter")

    def _render_markdown(self, config: NewsletterConfig, payload: dict, source_catalog: list[dict[str, str]]) -> str:
        section_title = config.sections[0] if config.sections else "Training Updates"
        source_by_id = {item["source_id"]: item for item in source_catalog}

        title = str(payload.get("title") or f"{config.topic} Training Newsletter").strip()
        opening_summary = str(payload.get("opening_summary") or "").strip()
        closing_takeaway = str(payload.get("closing_takeaway") or "").strip()
        raw_items = payload.get("items")
        items = raw_items if isinstance(raw_items, list) else []

        rendered_items: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            source_id = str(item.get("source_id") or "").strip()
            source = source_by_id.get(source_id)
            if not source:
                continue

            training = str(item.get("training") or source["title"]).strip()
            date_text = str(item.get("date") or source["published"]).strip()
            provider = str(item.get("provider") or source["source"]).strip()
            audience = str(item.get("audience") or "operators").strip()
            why_it_matters = str(item.get("why_it_matters") or source.get("summary", "")).strip()

            field_values = {
                "date": self._clean_field_value(date_text),
                "provider": self._clean_field_value(provider),
                "audience": self._clean_field_value(audience),
                "whyitmatters": self._clean_field_value(why_it_matters),
                "url": self._format_url(source["url"], config),
            }
            rendered_items.append(self._render_training_item(config, self._clean_field_value(training), field_values))

        if not rendered_items:
            for source in source_catalog[: max(1, min(5, len(source_catalog)))]:
                fallback_values = {
                    "date": self._clean_field_value(source["published"]),
                    "provider": self._clean_field_value(source["source"]),
                    "audience": "operators",
                    "whyitmatters": self._clean_field_value(source.get("summary", "")),
                    "url": self._format_url(source["url"], config),
                }
                rendered_items.append(
                    self._render_training_item(config, self._clean_field_value(source["title"]), fallback_values)
                )

        markdown_lines = [
            f"# {title}",
            "",
            opening_summary,
            "",
            f"## {section_title}",
            "",
            "\n\n".join(rendered_items),
        ]

        if closing_takeaway:
            markdown_lines.extend(["", "## Closing Takeaway", "", closing_takeaway])

        return "\n".join(markdown_lines).strip()

    def _render_training_item(self, config: NewsletterConfig, training: str, field_values: dict[str, str]) -> str:
        lines = [f"- **{config.output_item_label}:** {training}"]
        for field_name in config.output_fields:
            normalized = self._normalize_field_name(field_name)
            value = field_values.get(normalized, "")
            if not value:
                continue
            lines.append(f"\t- {field_name}: {value}")
        return "\n".join(lines)

    def _normalize_field_name(self, field_name: str) -> str:
        return re.sub(r"[^a-z]", "", field_name.lower())

    def _format_url(self, url: str, config: NewsletterConfig) -> str:
        style = config.url_style.strip().lower()
        if style == "raw":
            return url
        if style == "autolink":
            return f"<{url}>"
        return f"[{config.url_label}]({url})"

    def _clean_field_value(self, value: str) -> str:
        # Collapse all whitespace so markdown list spacing stays uniform.
        return " ".join(str(value).split())
