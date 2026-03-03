---
name: citation-assistant
description: >
  Automatic citation insertion for LaTeX manuscripts. Parses LaTeX source to find
  uncited statements (factual claims, method comparisons, background assertions,
  dataset references, numerical claims), searches for the correct papers via
  Semantic Scholar and DBLP, fetches official BibTeX (never fabricates), and inserts
  \cite{} commands. Returns modified .tex files and updated .bib file. Inspired by
  github.com/ZhangNy301/citation-assistant. Use when the user says "add citations",
  "find references for", "cite this", "my paper needs citations", or provides LaTeX
  files needing references.
user-invocable: true
argument-hint: "<path-to-tex-file> [additional .tex files...]"
---

## Overview

The citation-assistant skill automatically finds uncited claims in LaTeX manuscripts, searches for the right papers, fetches official BibTeX entries (never fabricates), and inserts `\cite{}` commands at the right locations. This eliminates the manual process of hunting down citations for statements, methods, datasets, and claims that lack proper attribution.

The skill uses a multi-stage pipeline:
1. Parse the LaTeX source to extract text content and existing citations
2. Identify statements that need citations but lack them
3. Generate targeted search queries for each identified location
4. Search academic databases (Semantic Scholar, DBLP, arXiv)
5. Fetch official BibTeX entries for the best-matching papers
6. Insert citations into the .tex files using the appropriate commands
7. Merge all BibTeX entries into a unified references file

## Input

One or more `.tex` file paths provided as arguments. The skill automatically:
- Detects existing `.bib` files in the same directory as the `.tex` files
- Parses `\bibliography{}` and `\addbibresource{}` commands to locate referenced bibliography files
- Reads all provided `.tex` files and any detected `.bib` files to understand the current citation state

## Setup

Install required dependencies using:

```bash
pip install -r BASE_DIR/scripts/requirements.txt
```

Ensure the following Python scripts are available in the `BASE_DIR/scripts/` directory:
- `paper_search.py` — searches Semantic Scholar and DBLP
- `bibtex_utils.py` — fetches and merges BibTeX entries

## Workflow

### Step 1: Parse LaTeX

Read all provided `.tex` files using the Read tool. Extract:
- All existing `\cite{}`, `\citep{}`, and `\citet{}` commands and their citation keys
- All `\bibliography{}` and `\addbibresource{}` references to locate bibliography files
- The full text content with LaTeX commands stripped for analysis
- Note the citation command style used in the document (to match in subsequent insertions)

### Step 2: Identify Uncited Statements

Scan the stripped text for statements that need citations but don't have them. Look for these patterns:

- **Related work indicators**: Sentences starting with "Recent work...", "Prior studies...", "It has been shown...", "Previous research...", "Earlier work...", "Other approaches..."
- **Comparison statements**: "X outperforms Y", "unlike previous methods", "compared to existing approaches", "superior to", "more effective than"
- **Dataset/benchmark mentions**: Explicit mentions without citations (e.g., "ImageNet", "GLUE", "MMLU", "MS COCO", "WikiText", "SQuAD")
- **Numerical claims**: "achieves X% accuracy on Y", "improves by X%", "reduces computational cost by", "Y% faster than"
- **Method names (proper nouns)**: "ResNet", "BERT", "GPT", "ViT", "CLIP", "Transformer", "ConvNet", "RNN", "LSTM" (if not already cited nearby)
- **Background assertions**: "Transformers have revolutionized...", "Attention mechanisms enable...", "Deep learning has become...", "Neural networks are known to..."

**Skip logic**: Do not flag locations that already have `\cite{}` within 2 sentences (they may be adequately cited).

### Step 3: Generate Search Queries

For each identified uncited location, construct a search query from the surrounding context (2-3 sentences). Focus on extracting:
- The specific claim or method name that needs a citation
- Key terms that would help identify the original paper
- The domain or field context if relevant

Example: For "ResNet has become the standard backbone for computer vision", generate query: "ResNet residual networks computer vision deep learning"

### Step 4: Search for Papers

For each query, run:

```bash
python "BASE_DIR/scripts/paper_search.py" --query "QUERY" --max-results 5 --sort citations
```

Parse the JSON output and select the most relevant paper based on:
- Title relevance to the claim (highest priority)
- Citation count (prefer well-established, widely-cited papers)
- Venue quality (prefer top-tier venues: NeurIPS, ICML, ICCV, ICLR, ACL, etc.)
- Recency (for "recent work" claims, prefer papers from last 3-5 years; for foundational work, recency is less important)

### Step 5: Fetch BibTeX

For each selected paper, run:

```bash
python "BASE_DIR/scripts/bibtex_utils.py" fetch --title "PAPER TITLE"
```

This fetches official BibTeX from Semantic Scholar → DBLP → arXiv in that order of preference. Never fabricate or manually construct BibTeX entries; if official sources fail, flag the entry as unconfirmed.

### Step 6: Insert Citations

For each identified uncited location:
- Insert `\cite{key}` at the appropriate position in the `.tex` file
- If multiple papers are needed for one statement, use `\cite{key1, key2}` or adapt to the document's citation style
- Match citation style to existing usage in the document:
  - `\cite{}` for basic citations
  - `\citep{}` for parenthetical citations (natbib style)
  - `\citet{}` for textual citations (natbib style)
- Write the modified `.tex` files to the output directory (do NOT overwrite originals)

### Step 7: Merge BibTeX

If an existing `.bib` file was found:

```bash
python "BASE_DIR/scripts/bibtex_utils.py" merge --inputs existing.bib new_entries.bib --output references.bib
```

Otherwise, create a new `references.bib` file with all new entries. Ensure:
- No duplicate keys
- All entries have complete required fields (author, title, year, etc.)
- Keys are consistent with the citations inserted in `.tex` files

## Edge Cases

- **Multiple papers needed**: Some statements legitimately reference multiple works → use `\cite{key1, key2}` or separate citations within 1-2 words of each other
- **Self-citations**: If the paper's own authors appear in search results, flag the citation with a note (optional inclusion) but still include it if relevant
- **Already cited nearby**: Skip locations where a relevant `\cite{}` appears within 2 sentences; the statement is likely already attributed
- **Ambiguous references**: When multiple candidate papers match equally well, prefer in order: higher citation count → more prestigious venue → more recent
- **No match found**: If `paper_search.py` returns no relevant results, note the location and original text in `changes.md` but do NOT insert a placeholder citation
- **Package conflicts**: Detect whether the document uses `natbib`, `biblatex`, or basic `bibtex` via `\usepackage{}` commands and use the appropriate citation command
- **Math/notation statements**: Skip pure mathematical or notational definitions that don't need citations (e.g., "Let x be a vector")

## Output

The skill produces three main outputs:

### 1. Modified `.tex` File(s)
- Saved to `output/citation-assistant/YYYY-MM-DD-HHMMSS/` directory
- Original file names preserved
- All uncited claims now have `\cite{}` commands inserted
- Original `.tex` files remain untouched

### 2. `references.bib`
- Complete bibliography file with all new entries merged
- Consistent formatting and key naming
- No duplicate entries
- Includes both existing citations and newly fetched ones

### 3. `changes.md`
Detailed changelog documenting every citation addition in table format:

```markdown
# Citation Changes

| # | Location (file:line) | Original Text | Added Citation | Paper Title | Reason |
|---|---------------------|---------------|----------------|-------------|--------|
| 1 | main.tex:45 | "Transformers have revolutionized..." | \cite{Vaswani2017} | Attention Is All You Need | Foundational work on transformers |
| 2 | main.tex:87 | "achieves 96.5% on ImageNet" | \cite{He2016} | Deep Residual Learning for Image Recognition | ImageNet dataset reference and method |
| 3 | related_work.tex:32 | "Recent work in NLP has focused on..." | \cite{Devlin2019,Radford2019} | BERT and GPT papers | Multiple relevant recent approaches |
| 4 | methods.tex:15 | "We use ResNet as backbone" | \cite{He2016} | Deep Residual Learning for Image Recognition | ResNet method reference |
```

Columns:
- **#**: Sequential number
- **Location (file:line)**: Which `.tex` file and approximate line number
- **Original Text**: The text that was missing a citation (first 50-80 characters)
- **Added Citation**: The exact `\cite{}` command inserted
- **Paper Title**: Full title of the cited paper
- **Reason**: Brief explanation (e.g., "Foundational work", "Method reference", "Dataset mention", "Comparison context")

## Output Directory

All outputs are saved to:

```
./output/citation-assistant/YYYY-MM-DD-HHMMSS/
```

With structure:
```
output/citation-assistant/2025-03-03-154230/
├── main.tex (modified)
├── methods.tex (modified)
├── related_work.tex (modified)
├── references.bib (new or merged)
└── changes.md (changelog)
```

## Tips

- **Iterative refinement**: Run this skill iteratively — the first pass catches obvious gaps (missing method citations, dataset references), the second pass catches subtler ones (background assertions, implicit comparisons)
- **Verification**: Always verify the fetched BibTeX entries are for the correct papers before finalizing; manually inspect `changes.md` to catch any incorrect matches
- **Section-specific strategies**:
  - **Survey/related-work sections**: Be more aggressive about finding citations; most claims should be cited
  - **Method/experiment sections**: Focus on citing specific techniques, algorithms, and datasets used
  - **Introduction**: Cite major foundational works and recent advances
  - **Conclusion**: Cite future work only if referencing specific papers; avoid vague citations
- **Citation density**: Aim for natural citation density (varies by field, but typically 1-3 citations per paragraph in related work, fewer in methods)
- **Author-date vs numeric**: Detect the citation system used and maintain consistency throughout
- **Key naming**: Ensure BibTeX keys are consistent with conventions (e.g., `AuthorYear` or `Author_et_al_Year`)
