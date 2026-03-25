---
name: newsletter-blueprint
description: "Use when: generating a US-only training-delivery newsletter for the past 90 days focused on manufacturing workforce curriculum and training programs."
metadata:
  sector_focus: "Manufacturing (General)"
  audience: "Plant managers, HR directors, industrial educators/trainers, apprenticeship coordinators, two-year college faculty, and trade school instructors"
  tone: "Technical, authoritative, and implementation-oriented"
  llm_provider: gemini
  llm_model: gemini-2.5-flash
  language: en-US
  max_articles: 12
  open_in_browser: true
  country_scope: "US"
  lookback_days: 90
  content_type: "Delivered trainings and curriculum programs only"
  output_item_label: "Training"
  output_fields:
    - Date
    - Provider
    - Audience
    - URL
    - Why it matters
  url_style: "wrapped_link"
  url_label: "Open source"
  sources:
    - https://news.google.com/rss/search?q=manufacturing+training+US+when:90d&hl=en-US&gl=US&ceid=US:en
  sections:
    - Delivered Training and Curriculum Programs (US, Last 90 Days)
---

# Workforce Development & Energy Efficiency Bulletin

Build a technical newsletter that reports only recently delivered US training and curriculum programs across general manufacturing.

# Editorial Requirements

- Include only US-based items from now back to the last 90 days.
- Include only training or curriculum that is delivered, launched, actively offered, planned with confirmed rollout dates, or completed with named participants.
- Valid training audiences are operators, apprenticeship learners, two-year college learners, trade school learners, or K-12 learners.
- Exclude policy-only, strategy-only, funding-only, and general commentary pieces.
- Exclude items that do not clearly identify a training provider.
- Exclude items without a publication date in the last 90 days.
- Prioritize concrete program announcements from manufacturers, colleges, school districts, training providers, and workforce boards.
- Prioritize direct-source items (manufacturer, college, training provider, workforce agency feeds) before Google News aggregation duplicates.

# Format Preferences

- Use exactly one section heading: "Delivered Training and Curriculum Programs (US, Last 90 Days)".
- Under that section, list each training as one top-level bullet and render sub-bullets based on frontmatter keys:
  - output_item_label
  - output_fields
  - url_style
  - url_label
- If no qualifying items are found, output: "No qualifying US training/curriculum items found in the last 90 days.".