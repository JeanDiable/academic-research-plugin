# Academic Research Plugin for Claude Code

A suite of 8 AI-powered academic workflow skills for Claude Code, designed for AI/ML PhD researchers.

## Installation

### Quick Install (Recommended)

```bash
# Add the marketplace
claude plugin marketplace add JeanDiable/academic-research-plugin

# Install the plugin
claude plugin install academic-research
```

### Manual Install

1. Clone this repository:

```bash
git clone https://github.com/JeanDiable/academic-research-plugin.git
```

2. Install Python dependencies:

```bash
pip install -r academic-research-plugin/lib/requirements.txt
```

3. Install the plugin in Claude Code:

```bash
claude plugin add /path/to/academic-research-plugin
```

### Optional

Set a Semantic Scholar API key for higher rate limits:

```bash
export S2_API_KEY="your-key-here"
```

## Skills

### 1. Literature Survey (`/academic-research:literature-survey`)

Comprehensive topic-driven literature survey. Searches arXiv, Semantic Scholar, and DBLP, identifies research gaps, performs cross-domain exploration, and proposes 2-3 innovation directions.

```
/academic-research:literature-survey "diffusion models for 3D generation"
```

### 2. Paper-Triggered Survey (`/academic-research:paper-triggered-survey`)

Anchored survey starting from a specific paper. Accepts PDF files, arXiv URLs, tweets, or paper titles. Maps the paper's research landscape and proposes extensions.

```
/academic-research:paper-triggered-survey https://arxiv.org/abs/2301.12345
/academic-research:paper-triggered-survey /path/to/paper.pdf
```

### 3. Survey Writing (`/academic-research:survey-writing`)

Taxonomy-focused survey paper drafting. Searches for papers, builds a multi-level taxonomy, and drafts a complete survey with introduction, per-category deep dives, comparison tables, and future directions.

```
/academic-research:survey-writing "vision-language models"
```

### 4. Paper Reviewing (`/academic-research:paper-reviewing`)

Conference-style peer review. Supports NeurIPS, ICML, CVPR, ACL, AAAI, ICCV, ICLR formats with adjustable severity. Generates structured reviews with scores, strengths, weaknesses, and questions.

```
/academic-research:paper-reviewing /path/to/submission.pdf
/academic-research:paper-reviewing /path/to/paper.pdf --venue neurips --severity balanced
```

### 5. Paper Polishing (`/academic-research:paper-polishing`)

Comprehensive draft feedback in ICML meta-review style. Analyzes correctness, motivation, methodology, presentation, visualizations, and citations. Outputs prioritized revision checklist.

```
/academic-research:paper-polishing /path/to/draft.pdf
```

### 6. Citation Assistant (`/academic-research:citation-assistant`)

Automatic citation insertion for LaTeX manuscripts. Finds uncited claims, searches for correct papers, fetches official BibTeX (never fabricates), and inserts `\cite{}` commands.

```
/academic-research:citation-assistant /path/to/paper.tex
```

### 7. Homework Machine (`/academic-research:homework-machine`)

End-to-end assignment completion. Analyzes requirements, conducts research, writes code with tests, drafts academic reports with citations, and performs paraphrasing via translation round-trip (macOS).

```
/academic-research:homework-machine /path/to/assignment.pdf
```

### 8. Poster & Slides Maker (`/academic-research:poster-slides-maker`)

Academic presentation creator. Generates conference-quality slides (reveal.js HTML) and/or posters (single-page HTML) from a paper PDF or LaTeX project. Standalone files viewable in any browser.

```
/academic-research:poster-slides-maker /path/to/paper.pdf --format slides --pages 15
/academic-research:poster-slides-maker /path/to/paper.pdf --format poster
```

## Project Structure

```
academic-research-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── lib/                          # Source of truth for shared utilities
│   ├── paper_search.py          # Unified search: arXiv + Semantic Scholar + DBLP
│   ├── bibtex_utils.py          # BibTeX fetch/merge/validate
│   ├── translate_roundtrip.py   # EN→ZH→EN paraphrasing (macOS)
│   └── requirements.txt         # Python dependencies
├── sync.sh                       # Copies lib/ to each skill's scripts/
├── skills/
│   ├── literature-survey/
│   │   ├── SKILL.md
│   │   └── scripts/             # Synced from lib/
│   ├── paper-triggered-survey/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── survey-writing/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── paper-reviewing/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── references/
│   │       └── conference_formats.md
│   ├── paper-polishing/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── citation-assistant/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── homework-machine/
│   │   ├── SKILL.md
│   │   └── scripts/             # Also includes translate_roundtrip.py
│   └── poster-slides-maker/
│       ├── SKILL.md
│       └── assets/
│           └── reveal-template.html
└── README.md
```

## Shared Utilities

### `paper_search.py`

Unified academic paper search across three sources:
- **arXiv** — Full-text search with metadata
- **Semantic Scholar** — Citation graph, abstracts, venue info
- **DBLP** — Conference/journal paper discovery

Features automatic deduplication (DOI exact match + fuzzy title matching at 0.85 threshold), configurable sorting, and JSON/text output.

### `bibtex_utils.py`

BibTeX reference management with a 3-source fallback chain: Semantic Scholar -> DBLP -> arXiv. Never fabricates entries — only fetches from official sources.

### `translate_roundtrip.py`

EN -> ZH -> EN translation round-trip for anti-plagiarism paraphrasing. Uses Google Translate for EN->ZH and Apple's macOS Translation framework for ZH->EN. Preserves technical terms via regex extraction.

## Development

After editing any file in `lib/`, run sync to distribute changes:

```bash
./sync.sh
```

## Requirements

- Claude Code
- Python 3.9+
- macOS (for `translate_roundtrip.py` Apple Translation — other features work cross-platform)
- Optional: `S2_API_KEY` environment variable for Semantic Scholar API

## License

MIT
