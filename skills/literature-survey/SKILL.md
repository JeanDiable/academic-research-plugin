---
name: literature-survey
description: >
  Comprehensive topic-driven literature survey for AI/ML research. Searches arXiv,
  Semantic Scholar, and DBLP for recent papers (default: last 1 year), identifies
  research gaps, performs cross-domain exploration, and proposes 2-3 innovation
  directions with feasibility assessment. Use this skill when the user wants to
  survey a research topic, find related work, identify research gaps, or generate
  research ideas. Also use when the user says "literature review", "related work
  search", "find papers about", or "what's the latest on".
user-invocable: true
argument-hint: "<topic> [--date-range 2y] [--max-papers 50] [--venues NeurIPS,ICML]"
---

# Literature Survey Skill

## Overview

The literature-survey skill performs a comprehensive topic-driven literature survey for AI/ML research. It systematically searches multiple academic databases (arXiv, Semantic Scholar, DBLP), identifies research gaps, performs cross-domain exploration to discover transferable methods, and proposes 2-3 innovation directions with detailed feasibility assessments.

## Arguments

Parse `$ARGUMENTS` as follows:

- **Topic (required)**: The first argument is the research topic string to survey. Example: `"vision transformer"`, `"graph neural networks"`, `"federated learning privacy"`.

- **--date-range** (optional): Time window for paper search. Default: `1y` (1 year). Supported values: `1y`, `2y`, `3y`. Controls the lookback period from today.

- **--max-papers** (optional): Maximum number of papers to retrieve per search query. Default: `50`. Useful for scoping large topics. Values: `10`-`200`.

- **--venues** (optional): Comma-separated list of conference/journal abbreviations to filter results. Example: `--venues NeurIPS,ICML,ICCV`. If omitted, all venues are included.

## Setup

This skill requires one-time dependency installation. Run:

```bash
pip install -r BASE_DIR/scripts/requirements.txt
```

Replace `BASE_DIR` with the base directory of the academic-research-plugin project (shown at the top of this skill's loaded context).

Required dependencies typically include:
- `requests` — for HTTP queries to research databases
- `arxiv` — Python client for arXiv API
- `bibtexparser` — for parsing and generating BibTeX
- `pandas` — for data aggregation and analysis

## Workflow

Follow these 7 steps to complete a comprehensive literature survey:

### Step 1: Decompose Topic into Search Queries

Break the user's topic into 3-5 focused search queries to capture different aspects and terminology variations:

- Use synonyms and alternative phrasing
- Include sub-problems and related terms
- Target specific methodologies, applications, and theoretical angles

**Example**: For "vision transformer", generate:
- `vision transformer`
- `ViT image classification`
- `self-attention computer vision`
- `visual attention mechanism`
- `transformer architecture image tasks`

Document all queries for reproducibility.

### Step 2: Execute Parallel Paper Searches

For each decomposed query, execute a paper search:

```bash
python BASE_DIR/scripts/paper_search.py --query "<query>" --max-results 20 --output json
```

- Each query searches up to 20 papers (scales with `--max-papers` flag from arguments)
- Output format: JSON with fields: `title`, `authors`, `year`, `venue`, `abstract`, `url`, `citations`
- Parse JSON results and aggregate papers across all queries
- Remove duplicates (same title or arXiv ID)
- Record the total number of papers found

### Step 3: Identify Seminal and Milestone Papers

Perform targeted searches for foundational works in the field:

- Search with a broader date range (e.g., last 5-10 years) to find seminal papers
- Manually identify must-read papers known in the field
- Example: For transformers, include "Attention Is All You Need" (Vaswani et al., 2017)
- Cross-reference high-citation papers (those cited 1000+ times)
- Mark seminal papers in the output with a "Seminal" label

### Step 4: Classify Papers into Themes and Identify Research Gaps

Organize all papers into 3-6 coherent sub-themes based on their core contributions:

**Sub-themes should cluster papers by**:
- Research methodology or technique
- Application domain
- Problem formulation
- Theoretical framework

For each theme, write a 2-3 sentence summary of the papers it contains.

**Research gaps** are identified by examining what is NOT covered:
- Missing combinations of techniques
- Unexplored application domains
- Unresolved theoretical questions
- Contradictions between papers
- Opportunities where existing methods haven't been tried

Document at least 3-5 distinct gaps with concrete descriptions.

### Step 5: Cross-Domain Exploration

Systematically search adjacent fields for transferable methodologies:

**Approach**:
1. Identify the core methodology or insight from papers in your main topic
2. Reframe it for adjacent domains (e.g., NLP→CV, CV→Audio, Supervised→Unsupervised)
3. Execute new searches in those domains with adapted keywords

**Example**: Vision Transformers (ViT)
- **Core insight**: Self-attention architecture from NLP (Transformers) applied to vision patches
- **Cross-domain queries**:
  - `"attention mechanism audio signal processing"`
  - `"transformer architecture time series forecasting"`
  - `"self-attention graph neural networks"`

Document findings that show successful methodology transfer and what made the transfer effective.

### Step 6: Propose Innovation Directions

Generate 2-3 concrete innovation proposals, each with:

- **Description**: 1-2 sentences explaining the core idea. Combine insights from gaps + cross-domain findings.

- **Feasibility Assessment**:
  - Data availability: Is sufficient labeled/unlabeled data accessible?
  - Compute requirements: GPU/TPU needs, training time estimates
  - Expected novelty: How different from existing work? Publication venue fit?
  - Timeline: Realistic implementation duration (weeks/months)

- **Potential Weaknesses**: Critical evaluation of limitations, edge cases, or reasons the idea might not work

- **Landing Plan**: Concrete first steps
  - What to implement first (MVP)
  - Expected intermediate milestones
  - Success metrics
  - Fallback strategy if initial approach fails

### Step 7: Collect BibTeX References

For all papers mentioned in the report, fetch complete BibTeX entries:

```bash
python BASE_DIR/scripts/bibtex_utils.py fetch --title "<paper_title>"
```

- Aggregate all BibTeX entries into a single `references.bib` file
- Use standard citation keys: `FirstAuthorYear` format (e.g., `vaswani2017`)
- Verify all references are parseable and contain required fields (author, title, year, venue)

## Output Format

Generate a comprehensive report file at `./output/literature-survey/YYYY-MM-DD-HHMMSS/survey_report.md` using this exact structure:

```markdown
# Literature Survey: <Topic>

**Date:** YYYY-MM-DD | **Papers Found:** N | **Date Range:** [e.g., "Last 1 year"] | **Search Queries:** K

## Paper Summary Table

| # | Title | Authors | Year | Venue | Citations | Notes |
|---|-------|---------|------|-------|-----------|-------|
| 1 | [Title with link to PDF/arXiv] | First Author et al. | YYYY | Conference/Journal | NNNN | Seminal / Key contribution |
| 2 | ... | ... | ... | ... | ... | ... |

---

## Theme Clusters

### Theme 1: <Name>

**Summary**: [2-3 sentences describing papers in this theme]

**Key Papers**:
- Paper A (Year)
- Paper B (Year)
- Paper C (Year)

**Contribution**: [What this theme contributes to the field]

### Theme 2: <Name>

[Same structure as Theme 1]

[Additional themes as needed...]

---

## Research Gaps

1. **Gap Name 1**: [Concrete description of missing research area or unresolved question]

2. **Gap Name 2**: [Another gap]

3. **Gap Name 3**: [Another gap]

[Additional gaps as identified...]

---

## Cross-Domain Findings

This section documents successful methodology transfer opportunities:

- **Finding 1**: [Methodology X from domain Y successfully applied to domain Z because of reason A. Example: Author Year]

- **Finding 2**: [Another cross-domain insight]

- **Finding 3**: [Another cross-domain insight]

---

## Innovation Proposals

### Proposal 1: <Innovation Title>

**Description**: [1-2 sentences of core idea]

**Feasibility**:
- Data: [Availability and requirements]
- Compute: [Estimated GPU/compute needs]
- Novelty: [How different from existing work, target venues]
- Timeline: [Realistic implementation duration]

**Potential Weaknesses**: [Critical evaluation of limitations and risks]

**Landing Plan**:
1. [First concrete step - MVP scope]
2. [Second step - intermediate milestone]
3. [Third step - validation/refinement]
- Success Metrics: [How to measure success]
- Fallback Strategy: [What to try if approach fails]

### Proposal 2: <Innovation Title>

[Same structure as Proposal 1]

### Proposal 3: <Innovation Title>

[Same structure as Proposal 1]

---

## References

See `references.bib` in this directory for complete BibTeX entries.

---

**Generated**: YYYY-MM-DD HH:MM:SS UTC | **Tool**: literature-survey skill v1.0
```

## Output Directory

All outputs are saved to:

```
./output/literature-survey/YYYY-MM-DD-HHMMSS/
```

The directory contains:
- `survey_report.md` — Main report with all findings and proposals
- `references.bib` — Complete BibTeX file with all cited papers
- `search_log.json` — Metadata on all executed searches (queries, result counts, dates)
- `papers_raw.json` — Full JSON dump of all retrieved papers for reference

## Tips for Best Results

1. **Topic Decomposition**: Spend time on Step 1. Better queries lead to more relevant papers.

2. **Date Range Selection**: Use `--date-range 3y` for emerging fields (last 3 years of rapid innovation). Use `1y` for stable fields with good coverage.

3. **Venue Filtering**: For rigorous surveys, use `--venues NeurIPS,ICML,ICCV,ICLR` to focus on top-tier venues.

4. **Seminal Papers**: Always manually verify that truly foundational papers are included, even if they're older.

5. **Gap Identification**: Gaps are most valuable when they're specific and actionable (i.e., suggest a concrete research direction rather than vague limitations).

6. **Innovation Proposals**: The best proposals combine insights from research gaps + cross-domain findings. Avoid purely speculative ideas.

7. **Feasibility Assessment**: Be honest about compute and data requirements. This makes proposals more credible and actionable.
