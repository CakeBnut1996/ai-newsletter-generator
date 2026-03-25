# AI Newsletter Generator

This project generates a topic-specific newsletter from a reusable skill file.

This project is managed with `uv`.

## What it does

- Reads your newsletter brief from `.github/skills/newsletter-blueprint/SKILL.md`
- Pulls fresh stories directly from RSS feeds and article pages
- Orchestrates story collection, article extraction, and AI drafting
- Writes the newsletter to Markdown and HTML
- Opens the latest HTML output when you run `main.py`

## Project layout

- `main.py`: command-line entry point
- `src/newsletter/news_service.py`: direct news feed and article-fetching helpers
- `src/newsletter/`: app logic
- `.github/skills/newsletter-blueprint/SKILL.md`: newsletter configuration

## Setup

1. Install dependencies and create the project environment:

```bash
uv sync
```

2. Put your API key in `.env`. This project defaults to Gemini and reads `GEMINI_API_KEY`.

## Configure the newsletter

Edit `.github/skills/newsletter-blueprint/SKILL.md` and change:

- `topic`
- `audience`
- `tone`
- `max_articles`
- `sections`
- `sources`
- `llm_provider`
- `llm_model`
- the editorial notes in the document body

If `sources` is empty, the project falls back to Google News RSS search for the topic.

## Run from the command line

```bash
uv run python main.py
```

This will:

1. Read the skill file
2. Gather articles from configured RSS feeds or Google News RSS
3. Ask Gemini to draft the newsletter
4. Save files in `output/`
5. Open the latest HTML file in your browser

## Manage dependencies

Add a package:

```bash
uv add <package-name>
```

Remove a package:

```bash
uv remove <package-name>
```

Update the environment after pulling changes:

```bash
uv sync
```

## Notes

- The generated files are written to `output/latest_newsletter.md` and `output/latest_newsletter.html`
- Older timestamped copies are also saved
- The app no longer requires MCP and runs as a plain Python project
- Dependencies are defined in `pyproject.toml` and managed with `uv`
