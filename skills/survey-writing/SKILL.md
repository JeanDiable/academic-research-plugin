---
name: survey-writing
description: >
  Taxonomy-focused literature review and survey paper writing. Given a research
  field or topic, searches comprehensively for papers, builds a multi-level taxonomy,
  and drafts a complete survey with introduction, background, per-category deep dives,
  comparison tables, and future directions. Unlike literature-survey, this skill focuses
  purely on organizing existing work — no cross-domain exploration or idea generation.
  Use when the user wants to "write a survey", "create a literature review", "organize
  papers into a taxonomy", or "draft a related work section".
user-invocable: true
argument-hint: "<field/topic> [--paper-count 100] [--date-range 3y] [--existing-papers paper1.pdf,paper2.pdf]"
---

## Overview

The survey-writing skill performs comprehensive survey composition by automating the research discovery and organization pipeline. It accepts a research topic, systematically searches for relevant papers across multiple query variations, constructs a hierarchical taxonomy of methodologies and approaches, drafts a publication-quality survey manuscript with narrative sections covering each category, generates comparison tables, and collects complete BibTeX metadata. The output is a structured survey paper suitable for direct submission or as a foundation for further refinement.

## Arguments

Parse the following arguments from the invocation string:

- **`<topic>`** (required) — The research field or topic to survey. Examples: "neural architecture search", "federated learning", "knowledge distillation in vision transformers". If ambiguous or overly broad (e.g., "machine learning"), ask the user to narrow the scope before proceeding.

- **`--paper-count`** (optional, default: 100) — Target number of unique papers to retrieve and analyze. Values typically range from 50 (narrow domain) to 200 (broad field).

- **`--date-range`** (optional, default: 3y) — Time window for paper publication. Format: `Ny` (years) or `Nm` (months), e.g., `5y`, `18m`, `2y6m`. Only retrieve papers published within this window.

- **`--existing-papers`** (optional) — Comma-separated list of local PDF file paths that the user has already collected. These PDFs will be parsed to extract titles and abstracts, which are incorporated into the survey for completeness. Format: `paper1.pdf,papers/paper2.pdf,/absolute/path/paper3.pdf`.

## Setup

Install dependencies once before running the workflow:

```bash
pip install -r "BASE_DIR/scripts/requirements.txt"
```

where `BASE_DIR` is the base directory for this skill, automatically injected by Claude Code.

## Workflow

### Step 1: Broad Paper Search

Decompose the research topic into 5–8 query variations covering synonyms, closely related sub-topics, and key methodologies relevant to the field.

For each query variation:
1. Run:
   ```bash
   python "BASE_DIR/scripts/paper_search.py" --query "<query>" --max-results <count/num_queries> --sort citations
   ```
   where `<count/num_queries>` is `--paper-count` divided by the number of queries (e.g., if 100 papers over 8 queries, use 13 per query).

2. Parse the results and combine into a single deduplicated list. Deduplicate by title and DOI when available.

3. If `--existing-papers` is provided, parse each PDF to extract its title and abstract. Add these papers to the combined list, marking them as "locally provided".

4. Save the complete paper list (with metadata: title, authors, year, abstract, citation count, venue, DOI) to `papers/search_results.json` for later reference.

### Step 2: Build Taxonomy

1. Read all paper abstracts and titles from the search results.

2. Manually or semi-automatically categorize papers into a hierarchical taxonomy with 2–4 levels:
   - **Level 1 (Top-level):** Approach types or problem categories (e.g., "Search Space Design", "Performance Prediction", "Hardware-aware NAS")
   - **Level 2 (Sub-categories):** Specific methodologies (e.g., "Reinforcement Learning", "Evolutionary Algorithms", "Gradient-based Methods")
   - **Level 3+ (Optional):** Further refinement for large categories

3. Ensure each leaf node contains at least 2 papers. If a category has only 1 paper, merge it with a sibling category that is most closely related conceptually.

4. Create an ASCII tree diagram representing the taxonomy structure, with category names and paper counts at each node. Example:

   ```
   Neural Architecture Search
   ├── Search Space Design (24 papers)
   │   ├── Cell-based (12 papers)
   │   ├── Layer-wise (8 papers)
   │   └── Hardware-aware (4 papers)
   ├── Search Strategies (35 papers)
   │   ├── Reinforcement Learning (18 papers)
   │   ├── Evolutionary Algorithms (12 papers)
   │   └── Gradient-based (5 papers)
   ├── Performance Prediction (20 papers)
   │   ├── Surrogate Models (14 papers)
   │   └── Early Stopping (6 papers)
   └── Efficiency & Hardware Co-design (21 papers)
       ├── Mobile/Edge (12 papers)
       └── FPGA/Specialized Hardware (9 papers)
   ```

5. Save this taxonomy to `taxonomy.txt` for reference.

### Step 3: Draft Survey Sections

Write a comprehensive survey manuscript with the following structure:

#### 1. Introduction & Motivation
Define the research field, explain why it matters, scope of the survey (time window, number of papers covered), and how it differs from prior surveys if applicable. End with a roadmap of subsequent sections.

#### 2. Background & Preliminaries
Introduce foundational concepts, notation, key definitions, and assumptions. For example, in a neural architecture search survey, this might cover what NAS is, why manual architecture design is expensive, and baseline approaches (e.g., inception modules, MobileNets).

#### 3. Taxonomy
Present the multi-level taxonomy hierarchy. Describe the decision criteria for each level. Justify the organization (e.g., "We organize by search strategy because the choice of strategy fundamentally determines efficiency and convergence").

#### 4 to N. Per-Category Deep Dives
For each top-level taxonomy category, create a section with subsections for each sub-category. Within each subsection:
- Describe the core idea and key methodologies
- Summarize 3–5 representative papers (names, key contributions, limitations)
- Explain the relationships among methods in that sub-category
- Discuss trade-offs (speed vs. accuracy, generalization, hardware requirements)

#### N+1. Comparison
Create one or more markdown tables comparing methods across shared benchmarks. Structure:
- **Rows:** Methods or papers
- **Columns:** Datasets/benchmarks, key metrics (accuracy, speed, memory, search cost)
- **Footnotes:** Highlight best performers per category

Example for a neural architecture search survey:
```
| Method | ImageNet Top-1 | ImageNet Latency (ms) | Proximal | Search Cost (GPU-days) |
|--------|----------------|-----------------------|----------|------------------------|
| ResNet-50 (baseline) | 76.5 | 54 | - | - |
| EfficientNet-B0 | 77.1 | 42 | - | - |
| DARTS | 77.3 | 51 | 93.4 | 8 |
| ENAS | 78.2 | 58 | 94.1 | 1.5 |
| ProxylessNAS | 78.5 | 46 | 94.3 | 12 |
```

#### N+2. Open Problems & Future Directions
Synthesize cross-cutting challenges and gaps identified across all categories. Propose concrete research directions. For example:
- "How can we transfer architectures across domains without extensive retraining?"
- "What are the fundamental limits of surrogate-based prediction?"
- "How do we design more hardware-aware search spaces for emerging accelerators?"

### Step 4: Collect BibTeX

For each cited paper in the survey:
1. Run:
   ```bash
   python "BASE_DIR/scripts/bibtex_utils.py" fetch --title "<PAPER_TITLE>"
   ```
   to retrieve BibTeX metadata. Save each result to a temporary `.bib` file.

2. Merge all `.bib` files:
   ```bash
   python "BASE_DIR/scripts/bibtex_utils.py" merge --inputs *.bib --output references.bib
   ```

3. Manually verify the merged BibTeX for consistency (check that all papers have titles, years, authors). Standardize venue abbreviations and author names.

## Survey Structure

The output survey markdown file must follow this exact template:

```markdown
# Survey: <Topic>

## 1. Introduction & Motivation

[Introduction content here]

## 2. Background & Preliminaries

[Background content here]

## 3. Taxonomy

[ASCII tree diagram]

[Description of taxonomy organization]

## 4. <Category 1>

### 4.1 <Sub-category 1>

[Content for sub-category 1]

### 4.2 <Sub-category 2>

[Content for sub-category 2]

## 5. <Category 2>

### 5.1 <Sub-category 1>

[Content for sub-category 1]

## [N]. Comparison

| Method | Metric1 | Metric2 | ... |
|--------|---------|---------|-----|
| [Row 1] | | | |
| [Row 2] | | | |

[Comparison notes and interpretation]

## [N+1]. Open Problems & Future Directions

[Future directions content]

## References

[BibTeX entries or formatted references]
```

## Output Directory

All output files are saved to:

```
./output/survey-writing/YYYY-MM-DD-HHMMSS/
```

where the timestamp is the start time of the survey generation.

Within this directory, create the following files:

- **`survey.md`** — The complete survey manuscript in markdown format, ready for sharing or submission.

- **`references.bib`** — A merged BibTeX file containing all cited papers. Each entry should use consistent citation keys in the format `FirstAuthorLastNameYear` (e.g., `Vaswani2017`, `Dosovitskiy2020`, `LiuYearofpub2021`).

- **`taxonomy.txt`** — The ASCII taxonomy tree diagram (extracted from Section 3 of the survey), saved as a standalone text file for quick reference.

- **`papers/`** — A directory containing JSON files with raw search results for each query variation. Files are named `query_1.json`, `query_2.json`, etc., with structure:
  ```json
  {
    "query": "original query string",
    "count": 42,
    "papers": [
      {
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "year": 2023,
        "abstract": "...",
        "venue": "NeurIPS",
        "citation_count": 15,
        "doi": "10.1234/example"
      }
    ]
  }
  ```

## Tips

- **Scope Management:** If the initial topic is extremely broad (e.g., "machine learning", "computer vision"), ask the user to narrow down the scope before beginning. A well-scoped survey covers 50–200 papers; attempting to cover thousands leads to shallow treatment.

- **Taxonomy Design:** Start by examining recent survey papers in the field (if any exist) to understand standard categorization schemes. Adapt and refine their taxonomies rather than inventing entirely new structures, as this aligns with community conventions.

- **Minimum Density:** Ensure each leaf category has at least 2 papers. Single-paper categories suggest the taxonomy is over-segmented and should be consolidated.

- **Comparison Tables:** Include at least one shared benchmark or metric in each comparison table (e.g., ImageNet accuracy, CIFAR-10 error rate). If papers use different benchmarks, create separate comparison tables per benchmark.

- **Citation Keys:** Use the format `FirstAuthorLastNameYear` consistently throughout the survey and BibTeX file. For papers with many authors, use only the first author's last name. For papers by organizations without individual authors, use a relevant acronym (e.g., `OpenAI2022`). Avoid spaces, special characters, and ambiguous abbreviations in citation keys.

- **Section Depth:** Aim for a balanced structure: 3–6 top-level categories with 2–4 sub-categories each. If the breakdown results in very shallow or very deep trees, adjust to achieve clarity.

- **Cross-References:** Within the survey text, explicitly cross-reference related work in other sections. For example: "As discussed in Section 5.2, surrogate-based methods often struggle with generalization across domains (see comparison in Section N)."

- **Iterative Refinement:** The first draft of the taxonomy may need adjustment after reading abstracts. Be prepared to re-organize if a category is over- or under-represented.
