from __future__ import annotations

from pathlib import Path
import sys

from dotenv import load_dotenv
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from newsletter import NewsletterOrchestrator, save_newsletter_outputs  # noqa: E402


load_dotenv(PROJECT_ROOT / ".env")

st.set_page_config(page_title="AI Newsletter Generator", layout="wide")
st.title("AI Newsletter Generator")
st.caption("Generate a recurring newsletter from the skill file and inspect the latest result.")

default_skill_path = PROJECT_ROOT / ".github" / "skills" / "newsletter-blueprint" / "SKILL.md"
skill_path = st.text_input("Skill file path", value=str(default_skill_path))


def run_generation(selected_skill_path: str):
    orchestrator = NewsletterOrchestrator(PROJECT_ROOT)
    package = orchestrator.generate_from_skill(selected_skill_path)
    return save_newsletter_outputs(package, PROJECT_ROOT / "output")


if st.button("Generate newsletter", type="primary"):
    with st.spinner("Collecting articles and drafting newsletter..."):
        package = run_generation(skill_path)
    st.success("Newsletter generated")
    st.subheader(package.title)
    st.markdown(package.markdown)

latest_markdown = PROJECT_ROOT / "output" / "latest_newsletter.md"
if latest_markdown.exists():
    st.divider()
    st.subheader("Latest saved newsletter")
    st.markdown(latest_markdown.read_text(encoding="utf-8"))