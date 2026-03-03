---
name: homework-machine
description: >
  End-to-end university assignment completion. Analyzes assignment requirements (PDF
  or text), conducts research, writes implementation code with tests, drafts an
  academic report (LaTeX or Word) with accurate citations, and performs automatic
  paraphrasing for anti-plagiarism via translation round-trip (macOS only). Use when
  the user provides a homework assignment, coursework, lab report requirements, or
  says "complete this assignment", "do my homework", "write this report", "finish
  this coursework".
user-invocable: true
argument-hint: "<assignment-pdf-or-text> [--format latex] [--language English]"
---

## Overview

The homework-machine skill provides an end-to-end pipeline for completing university assignments and coursework. It automates the entire workflow from requirement analysis through final deliverable assembly, including:

- **Requirement Analysis** — Parse assignment specifications and extract all deliverables
- **Research Phase** — Conduct literature search for background and methods
- **Code Implementation** — Write production-quality code with comprehensive tests
- **Report Writing** — Generate academic reports with proper citations and formatting
- **Paraphrasing** — Automatic anti-plagiarism via translation round-trip (macOS only)
- **Deliverable Assembly** — Collect all outputs with submission checklist

The workflow produces publication-ready reports, tested code, and all supporting materials needed for submission.

## Arguments

- `<assignment>` (required) — Path to assignment PDF or plain text file containing assignment requirements
- `--format` (optional, default: `latex`) — Output report format: `latex` or `docx`
- `--language` (optional, default: `English`) — Report writing language for the academic report

Example usage:
```bash
homework-machine /path/to/assignment.pdf --format latex --language English
homework-machine "assignment_text.txt" --format docx
```

## Setup

Before running this skill, ensure all dependencies are installed:

```bash
pip install -r "BASE_DIR/scripts/requirements.txt"
```

If using `.docx` output format, also install the Word document library:

```bash
pip install python-docx
```

Verify that the following helper scripts exist in `BASE_DIR/scripts/`:
- `paper_search.py` — Academic paper search and retrieval
- `bibtex_utils.py` — BibTeX citation management
- `translate_roundtrip.py` — Translation-based paraphrasing (macOS only)

## Workflow

The homework-machine executes 6 phases in sequence. After Phase 1, the user must explicitly confirm the plan before proceeding.

### Phase 1 — Analyze Assignment

1. **Read the Assignment**
   - If the input is a PDF, read it using appropriate tools
   - Paginate large PDFs (>20 pages) to avoid context overflow
   - If the input is a text file, read the entire content

2. **Extract Deliverables**
   - List all required outputs: academic report, source code, datasets, written answers, specific questions to address
   - Identify the format and structure expected for each deliverable

3. **Identify Constraints and Grading Criteria**
   - Page limits for the report
   - Specific format requirements (LaTeX template, Word template, etc.)
   - Required methods, algorithms, or frameworks
   - Expected citation count and style
   - Code submission format (single file, project structure, etc.)
   - Grading rubric if provided

4. **Present the Plan to User**
   - Summarize the assignment scope, deliverables, and constraints
   - Display estimated effort for each phase
   - Present the execution plan
   - **Wait for explicit user confirmation** before proceeding to Phase 2
   - Ask the user: "Are there any additional requirements or constraints not mentioned in the assignment that I should know about?"
   - Allow the user to add custom constraints, provide reference materials, or modify the scope

### Phase 2 — Research

1. **Conduct Literature Search**
   - Run the research command with the assignment topic:
     ```bash
     python "BASE_DIR/scripts/paper_search.py" --query "<assignment-topic>" --max-results 20 --sort citations
     ```
   - If the assignment mentions specific papers, methods, or techniques, run additional targeted searches

2. **Collect Findings**
   - Extract key concepts, mathematical formulations, and algorithms from top-cited papers
   - Identify foundational methods and state-of-the-art approaches relevant to the assignment
   - Note empirical results and benchmarks that will validate the implementation
   - Document all sources for later citation

3. **Organize Research Results**
   - Group findings by topic area (background, method, optimization, benchmarks, etc.)
   - Prioritize papers by relevance and citation count
   - Prepare to reference these in the report's Related Work section

### Phase 3 — Code Implementation

1. **Write Implementation Code**
   - Use Python as the default language unless the assignment specifies otherwise
   - Implement all required algorithms, data structures, and functionality per the assignment spec
   - Follow the specific requirements for methods, libraries, or frameworks mentioned in the assignment
   - Use clean, readable code with meaningful variable names
   - Add inline comments explaining the approach, key decisions, and non-obvious logic

2. **Write Test Cases**
   - Write comprehensive test cases that verify correctness
   - Test against expected outputs provided in the assignment
   - Test edge cases and boundary conditions
   - Ensure tests are isolated and reproducible
   - Aim for 80%+ code coverage

3. **Run and Verify**
   - Execute all tests and confirm they pass
   - Verify the implementation produces correct results
   - Check for runtime performance issues or memory leaks
   - Document any known limitations

4. **Save Code**
   - Save all source code files to the `code/` directory in the output
   - Include a `requirements.txt` if external packages are used
   - Include a `README.md` with instructions to run the code and tests

### Phase 4 — Report Writing

1. **Draft Academic Report**
   - Follow standard academic structure:
     - **Title & Abstract** — Concise summary of the problem and solution
     - **Introduction** — Problem statement, motivation, scope, and contributions
     - **Related Work / Background** — Review of relevant literature and methods (with citations)
     - **Method / Approach** — Detailed technical description of the solution with equations and pseudo-code where needed
     - **Experiments / Results** — Present findings, include tables, figures, and quantitative analysis
     - **Discussion** — Interpret results, discuss limitations, and suggest future work
     - **Conclusion** — Summarize key contributions and findings
     - **References** — Complete bibliography

2. **For LaTeX Format** (`--format latex`)
   - Use the LaTeX template provided in the Templates section below
   - Use article document class with standard packages
   - Include proper mathematical notation using amsmath
   - Ensure all figures and tables are properly referenced
   - Configure bibliography for natbib with numbered citations

3. **For DOCX Format** (`--format docx`)
   - Use the python-docx library to generate a Word document:
     ```python
     from docx import Document
     from docx.shared import Pt, RGBColor
     from docx.enum.text import WD_ALIGN_PARAGRAPH

     doc = Document()
     doc.add_heading('Your Title', 0)
     doc.add_paragraph('Your introduction text...')
     # ... add more content ...
     doc.save('report.docx')
     ```
   - Use proper heading hierarchy (Heading 1 for sections, Heading 2 for subsections)
   - Format tables with borders and shading for readability
   - Insert code blocks as formatted text or images
   - Use numbered and bulleted lists appropriately

4. **Fetch and Format Citations**
   - For each cited paper, retrieve the BibTeX entry:
     ```bash
     python "BASE_DIR/scripts/bibtex_utils.py" fetch --title "<paper-title>"
     ```
   - Collect all BibTeX entries into `references.bib`
   - Ensure author names, publication years, and venues are accurate
   - Use consistent citation style (numbered for LaTeX, author-date for Word)

5. **Accuracy and Depth**
   - Tailor report depth to assignment level (undergrad reports are typically 8-15 pages, graduate reports 15-30 pages)
   - Match technical depth to course level
   - Ensure all claims are supported by citations or experimental results
   - Verify mathematical correctness of equations

### Phase 5 — Paraphrase (macOS Only)

This phase uses Apple's built-in translation API to automatically rephrase content while preserving technical accuracy. It is only available on macOS systems with AppleScript support.

1. **Generate Technical Terms File**
   - Extract domain-specific terms from the assignment and report that should **NOT** be paraphrased:
     - Algorithm names (e.g., "QuickSort", "LSTM")
     - Method names from the assignment or code
     - Mathematical terms and notation
     - Proper nouns (author names, institution names)
     - Variable names and code identifiers
   - Save these as `terms.txt` in the output directory (one term per line)

2. **Paraphrase Substantial Paragraphs**
   - For each major paragraph in the report (excluding abstract, references, and code):
     ```bash
     python "BASE_DIR/scripts/translate_roundtrip.py" --input <paragraph_file> --terms-file terms.txt --diff
     ```
   - The script performs a round-trip translation (e.g., English → French → English) to generate varied phrasing
   - Technical terms are preserved by the terms file

3. **Review and Approve**
   - Display the diff for each paraphrased paragraph showing before/after versions
   - Verify that the paraphrased version:
     - Preserves technical accuracy
     - Maintains the original meaning
     - Varies sentence structure while keeping technical terms unchanged
     - Does not introduce errors in grammar or logic
   - Allow the user to accept or reject each paraphrase

4. **Error Handling**
   - If the script detects a non-macOS system, warn the user: "Paraphrasing requires macOS with AppleScript support. This feature will be skipped. Your report is complete but without automated paraphrasing."
   - If Apple Translate is unavailable or fails, skip this phase and continue to Phase 6
   - Save a copy of the original report before applying changes for recovery

5. **Apply Approved Changes**
   - Update the report with approved paraphrases
   - Save a `paraphrase_diff.md` showing all accepted before/after changes for reference

### Phase 6 — Assemble Deliverables

1. **Collect All Outputs**
   - Verify the output directory structure exists: `./output/homework-machine/YYYY-MM-DD-HHMMSS/`
   - Ensure all required deliverables from Phase 1 are present

2. **Directory Structure**
   ```
   ./output/homework-machine/2026-03-03-143025/
   ├── report.tex              (or report.docx if --format docx)
   ├── references.bib          (LaTeX) or bibliography data (docx)
   ├── code/
   │   ├── main.py
   │   ├── tests/
   │   │   └── test_main.py
   │   ├── requirements.txt
   │   └── README.md
   ├── terms.txt               (if paraphrasing ran)
   ├── paraphrase_diff.md      (if paraphrasing ran)
   └── checklist.md            (submission checklist)
   ```

3. **Generate Submission Checklist**
   - Create `checklist.md` with all required deliverables from the assignment
   - Mark each item as present/verified
   - Include file sizes and line counts for code files
   - Add notes on completeness and quality

4. **Final Verification**
   - Confirm all files are readable and properly formatted
   - Generate a summary report showing what was completed
   - Display the path to the output directory
   - Provide instructions for the user to review and submit

## LaTeX Template

Use this template as the foundation for LaTeX reports. If the assignment provides a specific LaTeX template, use that instead.

```latex
\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage[numbers]{natbib}
\usepackage{booktabs}

\title{Your Assignment Title}
\author{Your Name}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
Provide a concise summary of the problem, approach, and key results (150-250 words).
\end{abstract}

\section{Introduction}
\label{sec:intro}

Introduce the problem, explain its significance, and outline the scope of the work.
State the main contributions clearly.

\section{Related Work}
\label{sec:related}

Review relevant prior work and methods. Cite key papers using \cite{key}.

\section{Method / Approach}
\label{sec:method}

Describe the solution approach in detail. Include algorithms, pseudocode, and
mathematical formulations as needed.

\subsection{Algorithm Name}

Provide pseudocode or detailed steps here.

\section{Experiments and Results}
\label{sec:results}

Present experimental findings, results, and analysis.

\begin{table}[h]
\centering
\caption{Example Results Table}
\label{tab:results}
\begin{tabular}{lcc}
\toprule
Method & Accuracy & Time \\
\midrule
Baseline & 85\% & 0.5s \\
Proposed & 92\% & 0.6s \\
\bottomrule
\end{tabular}
\end{table}

\section{Discussion}
\label{sec:discussion}

Interpret the results, discuss limitations, and suggest directions for future work.

\section{Conclusion}
\label{sec:conclusion}

Summarize the key findings and contributions.

\bibliographystyle{plainnat}
\bibliography{references}

\end{document}
```

## Output Directory

All deliverables are saved to: `./output/homework-machine/YYYY-MM-DD-HHMMSS/`

The timestamp ensures each run creates a unique output directory. Contents include:

- **report.tex** or **report.docx** — The complete academic report ready for submission
- **references.bib** — BibTeX bibliography file (LaTeX) or embedded references (DOCX)
- **code/** — Directory containing all source code:
  - `main.py` or language-appropriate entry point
  - `tests/` subdirectory with test cases
  - `requirements.txt` listing dependencies
  - `README.md` with build and execution instructions
- **terms.txt** — Technical terms that were excluded from paraphrasing (if Phase 5 ran)
- **paraphrase_diff.md** — Before/after comparison of paraphrased sections (if Phase 5 ran)
- **checklist.md** — Final submission checklist verifying all deliverables

## Tips

1. **Always Confirm Before Heavy Work** — After Phase 1 analysis, present the plan to the user and wait for explicit confirmation. This prevents wasted effort if the user's understanding of the assignment differs.

2. **Match Report Depth to Assignment Level** — Undergraduate assignments typically expect 8-15 page reports with 15-25 citations, while graduate assignments often require 20-40 pages with 40+ citations. Adjust accordingly.

3. **Use Provided Templates** — If the assignment includes a specific LaTeX template or Word template, use it instead of the default template provided here. Adapt the structure to match instructor expectations.

4. **Test Code Before Writing About It** — Always run the implementation code and verify tests pass before writing the report. This ensures the reported results match actual behavior and prevents embarrassing discrepancies.

5. **Verify Citations** — Double-check BibTeX entries for accuracy, especially author names, publication years, and venues. Incorrect citations reflect poorly on academic work.

6. **Handle Paraphrasing Failures Gracefully** — If the paraphrasing script fails (non-macOS system, missing dependencies, API unavailability), the report is still complete and usable. Warn the user but continue to Phase 6.

7. **Request Clarification When Ambiguous** — If the assignment is unclear or contradictory, ask the user for clarification in Phase 1 before proceeding.

8. **Keep Code Separate from Report** — Maintain clean separation between implementation code in the `code/` directory and the report. Reference code in the report but don't embed large code blocks in the main text (use appendix or external files if needed).

9. **Document All Assumptions** — If you make assumptions about missing specifications (e.g., dataset sources, parameter choices), document them in the report's Method section or in the code README.

10. **Archive Outputs** — The timestamped output directory structure allows running the skill multiple times without overwriting previous work, enabling iterative refinement if needed.
