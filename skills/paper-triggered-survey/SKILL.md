---
name: paper-triggered-survey
description: >
  Paper-triggered literature survey and idea generation. Given a PDF, arXiv URL,
  or tweet containing a paper reference, analyzes the paper, searches for related
  work (including papers the input may have missed), performs cross-domain exploration,
  and proposes 2-3 innovation directions. Use when the user provides a specific paper
  and wants to understand its landscape, find extensions, or generate research ideas.
  Also triggers for "survey this paper", "what's related to this", "extend this work".
argument-hint: "<pdf-path | arxiv-url | tweet-url>"
---

# Paper-Triggered Survey Skill

## Overview

This skill performs a targeted literature survey anchored around a specific paper provided by the user. It combines:

- **Paper extraction and analysis** from multiple input formats (PDF, arXiv URL, tweet)
- **Citation graph traversal** to find citing and cited-by papers
- **Search-based discovery** of related work using extracted keywords
- **Cross-domain exploration** applying the paper's methodology to other domains
- **Innovation proposal generation** suggesting 2-3 extensions of the paper's work

The skill systematically maps the paper's research landscape, identifies gaps in cited work, and proposes novel research directions based on the paper's core contributions and methods.

## Input Detection

The skill automatically detects the input type from `$ARGUMENTS`:

- **PDF file** — Argument ends in `.pdf`
  - Read using Read tool with pagination (pages 1-20, then 21-40 for long papers)
  - Extract title, authors, abstract, key sections, and references

- **arXiv URL** — Argument contains `arxiv.org/abs/`
  - Extract paper ID from URL (e.g., `2301.12345`)
  - Use `paper_search.py` with `--arxiv-id` to fetch paper metadata and PDF

- **Tweet URL** — Argument contains `twitter.com` or `x.com`
  - Use WebFetch tool to extract tweet content
  - Parse for paper references (titles, arXiv IDs, DOIs)
  - Locate and load the referenced paper

- **Search query** — Any other format
  - Treat as paper title/topic search query
  - Run `paper_search.py --query` to find the paper
  - Load the first result or ask user to clarify

## Setup

Before running the skill, install dependencies:

```bash
pip install -r /Users/suizhi/Desktop/Research_Claude/academic-research-plugin/scripts/requirements.txt
```

Required packages:
- `arxiv` — arXiv API access
- `requests` — HTTP requests for paper fetching
- `bibtexparser` — BibTeX parsing and generation
- `semanticscholar` — Semantic Scholar API integration

## Workflow

### Step 1: Detect Input Type and Extract Paper

1. Parse `$ARGUMENTS` to determine input type
2. For PDF: Read file with tool, extracting title, authors, abstract
3. For arXiv URL: Extract ID and use `paper_search.py --arxiv-id <ID>` to fetch
4. For tweet: Use WebFetch to extract content, then locate referenced paper
5. For search query: Use `paper_search.py --query "<query>" --max-results 5` to find paper
6. Output: Confirmed paper metadata (title, authors, year, venue, arXiv ID, DOI)

### Step 2: Extract Key Concepts, Methods, Problem Formulation

From the paper's abstract, introduction, and methodology sections:

1. **Problem statement** — What problem does this paper solve?
2. **Core methods** — What techniques/algorithms are introduced?
3. **Key concepts** — Main ideas, theoretical foundations, technical terms
4. **Novelty** — How is this different from prior work?
5. **Results** — Main contributions and achievements
6. **Assumptions** — Key assumptions made in the work

Create a structured summary (200-300 words) capturing these elements.

### Step 3: Extract All Cited Works

Parse the references section of the paper:

1. Extract all cited paper titles, authors, years, venues
2. Identify citation count/relevance if available
3. Identify seminal works (highly cited in field)
4. Note which citations are to foundational work vs. concurrent work
5. Output: Structured list of references with metadata

### Step 4: Generate Search Queries

From extracted keywords and concepts, generate 3-5 targeted search queries:

1. **Direct methodology search** — e.g., "diffusion models image generation"
2. **Problem-focused search** — e.g., "image-to-image translation"
3. **Application domain search** — e.g., "conditional generation"
4. **Theoretical foundation search** — e.g., "denoising score matching"
5. **Recent advances search** — e.g., "diffusion models 2024"

Each query should be specific enough to find relevant papers while broad enough to discover related work.

### Step 5: Run Paper Search for Each Query

For each query generated in Step 4:

```bash
python /Users/suizhi/Desktop/Research_Claude/academic-research-plugin/scripts/paper_search.py \
  --query "<query>" \
  --max-results 20 \
  --output json \
  --sort relevance
```

Collect results and deduplicate across queries. Keep papers with relevance scores above threshold (e.g., 0.6).

### Step 6: Citation Graph Traversal

If Semantic Scholar paper ID available:

```bash
python /Users/suizhi/Desktop/Research_Claude/academic-research-plugin/scripts/paper_search.py \
  --paper-id <S2_ID> \
  --citing \
  --limit 50
```

```bash
python /Users/suizhi/Desktop/Research_Claude/academic-research-plugin/scripts/paper_search.py \
  --paper-id <S2_ID> \
  --cited-by \
  --limit 50
```

This finds:
- **Citing papers** — Work that builds on the anchor paper
- **Cited-by papers** — Foundational work the anchor paper builds upon

Extract 10-15 most relevant papers from each direction.

### Step 7: Identify Missing Related Work

Compare papers found in Steps 5-6 with paper's reference list:

1. Papers discovered by search but NOT cited by anchor paper
2. Categorize as:
   - Recent work (published after anchor paper) → May have been unavailable
   - Concurrent work (same year) → May have been overlooked
   - Prior work (before anchor) → Genuine gap in literature review
3. Suggest 2-3 papers per category that should have been cited

### Step 8: Cross-Domain Exploration

Identify the anchor paper's core methodology, then explore applications in other domains:

Example: Paper on diffusion models for image generation → Search for:
- Diffusion in audio/music generation
- Diffusion in 3D/mesh generation
- Diffusion in molecular design
- Diffusion in text generation
- Diffusion in video generation

Generate 3-5 cross-domain search queries and run Step 5 for each. Output innovative combinations not explored by anchor paper.

### Step 9: Propose Innovation Directions

Generate 2-3 innovation proposals extending the anchor paper. For each proposal include:

1. **Direction name** — Concise title
2. **Description** — 2-3 sentences explaining the idea
3. **Anchor connection** — How does it extend/build on anchor paper?
4. **Cross-domain insight** — If applicable, what cross-domain finding inspired this?
5. **Feasibility** — Low/Medium/High (can it be done in 3-6 months?)
6. **Weaknesses to overcome** — Technical challenges, theoretical gaps
7. **Landing plan** — Concrete first steps to validate idea

Base proposals on:
- Gaps identified in Step 7
- Cross-domain opportunities from Step 8
- Natural extensions of anchor paper's methodology
- Weaknesses or limitations noted in anchor paper

### Step 10: Collect BibTeX References

For all papers in final output, collect BibTeX entries:

```bash
python /Users/suizhi/Desktop/Research_Claude/academic-research-plugin/scripts/bibtex_utils.py \
  fetch \
  --title "<paper-title>"
```

If `bibtex_utils.py` unavailable, manually format BibTeX from collected metadata.

## Output Format

Save results to timestamped directory: `./output/paper-triggered-survey/YYYY-MM-DD-HHMMSS/`

Create `survey-report.md` with the following structure:

```markdown
# Paper-Triggered Survey

## Anchor Paper

**Title:** [Full title]
**Authors:** [Author list]
**Year:** [YYYY]
**Venue:** [Conference/Journal]
**arXiv ID:** [Optional]
**DOI:** [Optional]

### Problem Formulation
[2-3 sentences on the core problem]

### Core Methods
[Bullet list of main techniques introduced]

### Key Concepts
[Bullet list of important ideas/terms]

### Main Contributions
[2-3 sentence summary of contributions]

---

## Step 2: Extracted Concepts & Methods

**Problem Statement:** [Detailed problem description]

**Methodology Overview:**
[Technical approach description, 150-200 words]

**Key Terms & Concepts:**
- Term 1: Definition
- Term 2: Definition
- (Continue for 8-10 key terms)

**Novelty vs. Prior Work:** [How this differs from related work]

---

## Step 3: Referenced Works Summary

**Total References:** [N]

**Seminal Works (Highly Cited):**
| Title | Authors | Year | Citation Count |
|-------|---------|------|-----------------|

**Foundational Works:**
[Bullet list of 5-7 most important cited papers]

---

## Step 5: Related Work Discovered (N papers)

| # | Title | Authors | Year | Venue | Citations | Relevance | Relation to Anchor |
|---|-------|---------|------|-------|-----------|-----------|-------------------|
| 1 | ... | ... | ... | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... | ... | ... | ... |
| (Continue for all discovered papers) |

**Search Queries Used:**
1. Query 1 → N results
2. Query 2 → N results
3. (List all queries and result counts)

---

## Step 6: Citation Graph Analysis

### Papers Citing the Anchor Paper (N papers)
[List 5-10 most relevant papers that cite anchor, with brief relevance notes]

### Papers Cited by the Anchor Paper (N papers)
[Sampling of most important foundational papers cited, organized by category]

---

## Step 7: Missing Related Work

Papers the anchor should have cited but didn't:

**Recent Work (Published After Anchor):**
| Title | Authors | Year | Why Relevant |
|-------|---------|------|--------------|
| ... | ... | ... | ... |

**Concurrent Work (Same Year as Anchor):**
| Title | Authors | Year | Why Relevant |
|-------|---------|------|--------------|
| ... | ... | ... | ... |

**Prior Work (Gaps in Literature Review):**
| Title | Authors | Year | Why Relevant |
|-------|---------|------|--------------|
| ... | ... | ... | ... |

---

## Step 8: Cross-Domain Exploration

### Domain Extension: [Domain 1]
**Query:** [Search query used]
**Findings:** [2-3 key papers showing how anchor's methodology applies]
**Innovation Opportunity:** [Brief insight on how methodology could transfer]

### Domain Extension: [Domain 2]
**Query:** [Search query used]
**Findings:** [2-3 key papers]
**Innovation Opportunity:** [Brief insight]

### Domain Extension: [Domain 3]
**Query:** [Search query used]
**Findings:** [2-3 key papers]
**Innovation Opportunity:** [Brief insight]

---

## Step 9: Innovation Proposals

### Proposal 1: [Direction Name]

**Description:**
[2-3 sentences describing the research direction]

**Connection to Anchor Paper:**
[How it extends/builds on the anchor work]

**Cross-Domain Insight:**
[Which cross-domain finding inspired this, if any]

**Feasibility:** [Low/Medium/High]
- **Timeline:** [Estimated months to validate]
- **Required Resources:** [Key skills, datasets, compute needed]

**Weaknesses to Overcome:**
1. Challenge 1: [Description and mitigation]
2. Challenge 2: [Description and mitigation]
3. Challenge 3: [Description and mitigation]

**Landing Plan:**
1. Month 1-2: [Validation step 1]
2. Month 3-4: [Implementation step 1]
3. Month 5-6: [Evaluation/publication]

**Key References:**
- [Related papers from discovery phase]

---

### Proposal 2: [Direction Name]

[Same structure as Proposal 1]

---

### Proposal 3: [Direction Name]

[Same structure as Proposal 1]

---

## Step 10: Bibliography

Complete BibTeX for all papers referenced in this survey:

\`\`\`bibtex
@article{anchor2024title,
  title={Full Title},
  author={Author, A. and Author, B.},
  journal={Journal Name},
  year={2024},
  volume={1},
  pages={1-20}
}

[Continue for all papers]
\`\`\`

---

## Metadata

**Survey Generated:** [Timestamp]
**Total Papers Found:** [N]
**Total Proposals Generated:** 3
**Base Directory:** /Users/suizhi/Desktop/Research_Claude/academic-research-plugin
```

## Output Directory Structure

```
./output/paper-triggered-survey/YYYY-MM-DD-HHMMSS/
├── survey-report.md           # Main report (above structure)
├── anchor-paper.pdf           # Copy of anchor paper if available
├── related-papers/
│   ├── cited-by.json          # Papers citing the anchor
│   └── citing.json            # Papers cited by anchor
├── search-results/
│   ├── query-1-results.json
│   ├── query-2-results.json
│   └── query-N-results.json
├── cross-domain/
│   ├── domain-1.json
│   ├── domain-2.json
│   └── domain-3.json
└── bibtex/
    └── all-papers.bib         # Complete bibliography
```

## Usage Examples

**Trigger 1: Direct PDF**
```
/paper-triggered-survey /path/to/paper.pdf
```

**Trigger 2: arXiv URL**
```
/paper-triggered-survey https://arxiv.org/abs/2301.12345
```

**Trigger 3: Tweet with paper**
```
/paper-triggered-survey https://x.com/user/status/123456789
```

**Trigger 4: Paper title**
```
/paper-triggered-survey "Diffusion Models Beat GANs on Image Synthesis"
```

**Trigger 5: Suggested usage**
```
User: "Survey this paper: https://arxiv.org/abs/2306.06465"
→ Activates paper-triggered-survey skill
```

## Key Features

1. **Multi-format input** — Handles PDFs, arXiv URLs, tweets, and search queries
2. **Comprehensive search** — Combines keyword search, citation graphs, and cross-domain exploration
3. **Gap analysis** — Identifies papers that should have been cited but weren't
4. **Innovation-focused** — Proposes concrete research directions with landing plans
5. **Structured output** — Reports organized for immediate research use
6. **Timestamped output** — Enables tracking of multiple surveys on same paper

## Dependencies

- `paper_search.py` — Core search utility with arXiv and Semantic Scholar integration
- `bibtex_utils.py` — BibTeX reference management (if available)
- Claude Read tool — PDF extraction
- Claude WebFetch tool — Tweet/URL content extraction
- `requirements.txt` — Python package dependencies

## Error Handling

- **Paper not found:** Report and suggest alternative searches or user clarification
- **Missing references section:** Use metadata from search results as fallback
- **API rate limits:** Implement delays, report gracefully
- **Large PDFs:** Paginate reading (first 20 pages, then 21-40, etc.)
- **Malformed input:** Validate URLs, file paths; suggest corrections

## Notes

- For very recent papers (< 3 months old), Semantic Scholar citation data may be incomplete
- Cross-domain exploration queries should balance specificity and discovery
- Innovation proposals should be evaluated for novelty, feasibility, and alignment with anchor paper
- Survey quality depends on quality of extracted keywords in Step 4
