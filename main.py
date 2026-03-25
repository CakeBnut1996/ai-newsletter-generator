from __future__ import annotations

import argparse
from pathlib import Path
import sys
import webbrowser

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from newsletter import NewsletterOrchestrator, load_newsletter_config, save_newsletter_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a newsletter from the configured skill file")
    parser.add_argument(
        "--skill-path",
        default=str(PROJECT_ROOT / ".github" / "skills" / "newsletter-blueprint" / "SKILL.md"),
        help="Path to the newsletter skill file",
    )
    return parser.parse_args()


def run(skill_path: str) -> None:
    config = load_newsletter_config(skill_path)
    orchestrator = NewsletterOrchestrator(PROJECT_ROOT)
    package = orchestrator.generate(config)
    package = save_newsletter_outputs(package, PROJECT_ROOT / "output")
    print(f"Generated: {package.markdown_path}")
    print(f"Rendered: {package.html_path}")

    if config.open_in_browser and package.html_path:
        webbrowser.open(package.html_path.as_uri())


if __name__ == "__main__":
    load_dotenv(PROJECT_ROOT / ".env")
    args = parse_args()
    run(args.skill_path)
