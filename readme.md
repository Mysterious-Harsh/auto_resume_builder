# Auto Resume Builder

Lightweight utility for generating, analyzing, and formatting resumes using a set of modular agents and a local Chroma vector store.

## Quick links
- Entry point: [main.py](main.py)  
- Packaging: [setup.py](setup.py)  
- Environment file: [.env](.env) (contains API keys — do NOT commit real secrets)  
- Master resume data: [data/master_background.json](data/master_background.json)  
- Local Chroma DB: [data/chroma_data/chroma.sqlite3](data/chroma_data/chroma.sqlite3)

## What this project does
- Stores structured master background data in [data/master_background.json](data/master_background.json).
- Indexes content and embeddings into a local Chroma DB ([data/chroma_data/chroma.sqlite3](data/chroma_data/chroma.sqlite3)).
- Provides agents to scrape, index, rephrase, analyze, score for ATS, organize content, and generate PDFs.

## Core components

Agents (see source for details):
- [`agents.scraper_agent`](agents/scraper_agent.py) — scrapes job/descriptions or web content.
- [`agents.indexing_agent`](agents/indexing_agent.py) — builds/updates Chroma index from master data.
- [`agents.analysis_agent`](agents/analysis_agent.py) — analyzes job text and resume bullets.
- [`agents.rephrasing_agent`](agents/rephrasing_agent.py) — rewrites/rephrases bullets.
- [`agents.ats_score_agent`](agents/ats_score_agent.py) — computes ATS fit/score.
- [`agents.organize_agent`](agents/organize_agent.py) — organizes content for output.
- [`agents.pdf_agent`](agents/pdf_agent.py) — renders final PDF (see [misc/PDF_Tests.ipynb](misc/PDF_Tests.ipynb) and tests in [tests/test_pdf_agent.py](tests/test_pdf_agent.py)).

Core utilities:
- Configuration: [core/config.py](core/config.py)
- Data models: see [`core.data_models.MetaData`](core/data_models.py) for metadata stored in vector DB.

## Setup & usage

1. Install (editable):
```sh
python -m pip install -e .