from __future__ import annotations

from datetime import datetime
from pathlib import Path

import markdown

from .models import NewsletterPackage


def build_html_document(title: str, markdown_content: str) -> str:
    body_html = markdown.markdown(
        markdown_content,
        extensions=["extra", "tables", "sane_lists"],
    )
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4efe5;
      --panel: #fffaf2;
      --ink: #1f1d1a;
      --accent: #0f766e;
      --muted: #6b665e;
      --border: #d8cebd;
    }}
    body {{
      margin: 0;
      background: radial-gradient(circle at top, #fff4d6 0%, var(--bg) 48%, #efe7da 100%);
      color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.65;
    }}
    main {{
      max-width: 840px;
      margin: 40px auto;
      padding: 40px;
      background: rgba(255, 250, 242, 0.92);
      border: 1px solid var(--border);
      box-shadow: 0 24px 60px rgba(31, 29, 26, 0.08);
      border-radius: 24px;
      backdrop-filter: blur(8px);
    }}
    h1, h2, h3 {{
      font-family: "Palatino Linotype", Georgia, serif;
      line-height: 1.2;
    }}
    h1 {{
      font-size: 2.5rem;
      margin-top: 0;
    }}
    h2 {{
      margin-top: 2.2rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
    }}
    a {{
      color: var(--accent);
    }}
    p, li {{
      font-size: 1.04rem;
    }}
    code {{
      background: #efe4d1;
      padding: 0.15rem 0.35rem;
      border-radius: 6px;
    }}
    blockquote {{
      border-left: 4px solid var(--accent);
      margin-left: 0;
      padding-left: 1rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    {body_html}
  </main>
</body>
</html>
""".strip()


def save_newsletter_outputs(package: NewsletterPackage, output_dir: str | Path) -> NewsletterPackage:
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    dated_markdown = base_path / f"newsletter_{timestamp}.md"
    dated_html = base_path / f"newsletter_{timestamp}.html"
    latest_markdown = base_path / "latest_newsletter.md"
    latest_html = base_path / "latest_newsletter.html"

    for path, content in [
        (dated_markdown, package.markdown),
        (dated_html, package.html),
        (latest_markdown, package.markdown),
        (latest_html, package.html),
    ]:
        path.write_text(content, encoding="utf-8")

    package.markdown_path = latest_markdown
    package.html_path = latest_html
    return package
