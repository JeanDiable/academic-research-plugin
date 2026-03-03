---
name: paper-polishing
description: >
  Comprehensive academic paper draft feedback in ICML meta-review style. Analyzes
  correctness (equations, proofs, notation), motivation, methodology gaps, presentation
  quality, visualization improvements, and missing citations. Outputs structured feedback
  with overall assessment, strengths, critical/major issues, section-by-section comments,
  and a prioritized revision checklist. Use when the user wants "feedback on my paper",
  "polish my draft", "review my manuscript", "what should I improve", or "help me revise".
user-invocable: true
argument-hint: "<pdf-path>"
---

# Paper Polishing Skill

## Overview

Unlike the paper-reviewing skill (which simulates a formal conference reviewer), this skill acts as a **constructive advisor** helping the author improve their draft. It provides actionable feedback with specific suggestions for improvement, not just criticism. The goal is to identify gaps in correctness, motivation, methodology, presentation, and citations, then guide the author toward a stronger submission.

**Key Differences from Paper Review:**
- **Tone**: Supportive and solutions-oriented, not evaluative
- **Depth**: Focuses on what can be improved, with concrete fix suggestions
- **Scope**: Covers technical correctness, clarity, impact, and presentation quality
- **Output**: Actionable revision checklist prioritized by severity

## Setup

Before running this skill, ensure dependencies are installed:

```bash
pip install -r BASE_DIR/scripts/requirements.txt
```

This installs required libraries for PDF processing, citation retrieval, and analysis.

## Workflow

The paper polishing process consists of three main phases: comprehensive reading, multi-angle analysis, and synthesis.

### Phase 1: Read Full Paper

Use the Read tool with pagination to process the entire PDF:
- Break large papers into 20-page chunks (pages 1-20, then 21-40, etc.)
- As you read, take structured notes on:

**Paper Metadata:**
- Paper title and authors
- Target venue/journal
- Abstract summary

**Technical Elements:**
- List of ALL equations (record equation numbers, variable definitions, notation)
- List of ALL theorems, lemmas, propositions, corollaries (with full statements and conditions)
- List of ALL figures with descriptions and captions
- List of ALL tables with descriptions and captions

**Content Tracking:**
- Key claims and their location in the paper
- Main contributions stated explicitly
- Notation used throughout (build a complete notation table)
- Assumptions made (stated and unstated)
- Baseline methods compared

### Phase 2: Multi-Angle Analysis

Analyze the paper from six complementary angles:

#### 2.1 Correctness Analysis
- **Equation verification**: For every equation, check:
  - Dimensional consistency (do all terms have the same units?)
  - Variable definitions (is every variable defined before use?)
  - Notation conflicts (is any symbol reused with different meanings?)
  - Algebraic correctness (are simplifications valid?)
  - Off-by-one errors (especially in indices and ranges)
- **Theorem/Lemma statements**: Verify:
  - Are all conditions sufficient for the conclusion?
  - Are conclusions precise and not overstated?
  - Are there unstated assumptions (boundedness, continuity, etc.)?
  - Do proofs match statements?
- **Technical soundness**: Identify logical gaps in reasoning, missing derivations, or unjustified leaps

#### 2.2 Motivation Analysis
- **Research gap**: Is the specific problem clearly articulated? (Not just "performance is important")
- **Novelty**: Are contributions specific and falsifiable? Avoid vague statements like "we improve performance" — flag these for concrete metrics
- **Positioning**: Does the introduction tell a compelling story? Does it build from prior work to the specific gap?
- **Impact**: Is it clear why solving this problem matters?

#### 2.3 Methodology Analysis
- **Approach soundness**: Identify logical holes or oversimplifications in the proposed method
- **Ablation studies**: Which components contribute to performance? Are ablations comprehensive?
- **Baseline fairness**: Are comparisons fair (same data, same computational budget, same tuning effort)?
- **Result claims**: Are claims overstated? Look for phrases like "state-of-the-art" without comprehensive comparison
- **Reproducibility**: Are implementation details sufficient? Can someone reproduce results?

#### 2.4 Presentation Analysis
- **Readability**: Is the paper easy to follow? Are sections logically ordered?
- **Redundancy**: Is content repeated unnecessarily?
- **Figure/Table usage**: Is every figure and table referenced in text? Does each serve a clear purpose?
- **Acronyms**: Are all acronyms defined on first use?
- **Abstract alignment**: Does the abstract match the actual contributions in the paper?
- **Writing quality**: Are sentences clear and concise? Are there grammatical issues?

#### 2.5 Visualization Analysis
For **EACH** figure and table, provide specific improvement suggestions:
- **Current state**: Describe what is shown
- **Suggested improvements**: Be specific with actionable changes
  - Layout and positioning
  - Color scheme (suggest colorblind-friendly palettes when relevant)
  - Axis labels and legends
  - Font sizes (recommend minimum 11pt for readability)
  - Data to add, remove, or highlight
  - Chart type changes (e.g., "Use box plots instead of bar charts to show distribution")
  - Size and aspect ratio adjustments
- **Example format**: "Figure 3: Add error bars to show uncertainty, increase font size to 12pt, use #1f77b4, #ff7f0e palette for colorblind accessibility"

#### 2.6 Missing Citations Analysis
For each major technical claim, baseline comparison, or methodological choice:
- Run: `python BASE_DIR/scripts/paper_search.py --query "<claim-related-query>" --max-results 5 --sort citations`
- Identify seminal papers that should be cited
- Note exact locations where citations should be inserted
- Explain why each suggested citation strengthens the paper
- Record results in structured format for output

### Phase 3: Synthesize Findings

Compile all findings into the structured output format, organized by severity:

**Priority Levels:**
- **Critical**: Would likely cause rejection or major rejection decision. Must be fixed before submission.
- **Major**: Significantly weakens the paper and should be addressed before submission.
- **Minor**: Nice-to-have improvements that would strengthen presentation or clarity.

Create a prioritized revision checklist ordered from critical to minor issues.

## Output Format

Generate a comprehensive report following this structure:

```
# Paper Polishing Report: <Paper Title>

## Overall Assessment
**Recommendation:** [Accept / Minor Revision / Major Revision / Not Ready]
**Justification:** [2-3 sentences explaining the assessment and what changes would strengthen it]

## Top 3 Strengths
1. [Specific strength with concrete evidence from the paper]
2. [Specific strength with concrete evidence from the paper]
3. [Specific strength with concrete evidence from the paper]

## Critical Issues (must fix before submission)
1. **[Issue Title]**: [Section/Page reference] — [Explanation of the problem] — [Concrete suggested fix]
2. **[Issue Title]**: [Section/Page reference] — [Explanation of the problem] — [Concrete suggested fix]
3. [Continue as needed...]

## Major Issues (significantly weaken the paper)
1. **[Issue Title]**: [Section/Page reference] — [Explanation of the problem] — [Concrete suggested fix]
2. **[Issue Title]**: [Section/Page reference] — [Explanation of the problem] — [Concrete suggested fix]
3. [Continue as needed...]

## Section-by-Section Feedback

### Abstract
- [Observation 1]: [Specific suggestion]
- [Observation 2]: [Specific suggestion]
- [If no issues, state "Well-written abstract that clearly conveys contributions"]

### 1. Introduction
- [Observation 1]: [Specific suggestion]
- [Observation 2]: [Specific suggestion]
- [Continue for all sections...]

### 2. Related Work
- [Observation 1]: [Specific suggestion]

### 3. Method
- [Observation 1]: [Specific suggestion]

### 4. Experiments
- [Observation 1]: [Specific suggestion]

### 5. Conclusion
- [Observation 1]: [Specific suggestion]

[Add sections for any additional major sections like Discussion, Appendix, etc.]

## Equation Review
| Eq. # | Issue | Suggestion |
|-------|-------|------------|
| (1) | [Issue if any] | [Corrected version or clarification] |
| (2) | [Issue if any] | [Corrected version or clarification] |

[Include all equations with issues; omit table if no issues found]

## Figure & Table Review
| Item | Current State | Suggested Improvement |
|------|--------------|----------------------|
| Figure 1 | [Description of what is shown] | [Specific actionable improvement] |
| Table 1 | [Description of what is shown] | [Specific actionable improvement] |
| Figure 2 | [Description of what is shown] | [Specific actionable improvement] |

[Include all figures and tables with suggested improvements]

## Missing Citations
| Location | Statement/Claim | Suggested Citation | Why It Should Be Cited |
|----------|-----------------|-------------------|----------------------|
| Sec 2, p.3 | "Method X is commonly used..." | Citation 1: Author et al. (Year) | Seminal work establishing method X |
| Sec 3, p.5 | "We compare against baseline Y" | Citation 2: Author et al. (Year) | Original paper introducing baseline Y |

[Include citations found to be missing; omit table if no critical gaps found]

## Revision Checklist

- [ ] **Priority 1 (Critical):** [Action item with specific location/instruction]
- [ ] **Priority 2 (Critical):** [Action item with specific location/instruction]
- [ ] **Priority 3 (Critical):** [Action item with specific location/instruction]
- [ ] **Priority 4 (Major):** [Action item with specific location/instruction]
- [ ] **Priority 5 (Major):** [Action item with specific location/instruction]
- [ ] **Priority 6 (Minor):** [Action item with specific location/instruction]
- [ ] **Priority 7 (Minor):** [Action item with specific location/instruction]

[Continue as needed; order strictly from critical to minor]
```

## Output Directory Structure

Save all outputs to `./output/paper-polishing/YYYY-MM-DD-HHMMSS/` with:

- **`feedback.md`**: The complete polishing report following the format above
- **`missing_citations.json`**: Structured citation search results in format:
  ```json
  {
    "paper_title": "...",
    "analysis_timestamp": "...",
    "missing_citations": [
      {
        "location": "Section 2, page 3",
        "claim": "Method X is the standard approach",
        "suggested_citations": [
          {
            "title": "...",
            "authors": "...",
            "year": 2023,
            "venue": "...",
            "reason": "Seminal work establishing this method",
            "search_query": "..."
          }
        ]
      }
    ]
  }
  ```

## Best Practices & Tips

### Be Constructively Critical
- Always suggest specific fixes, not just identify problems
- Phrase suggestions as improvements, not deficiencies
- If a section is weak, explain how to strengthen it

### Equation Handling
- When flagging an equation issue, provide the corrected version
- Use proper LaTeX notation in feedback
- Flag inconsistencies in notation between equations

### Early-Stage Papers
- If the paper is clearly early-stage (incomplete sections, preliminary results), focus on structural issues rather than polish
- Suggest reorganization and major gaps rather than sentence-level edits
- Identify what needs to be added for the paper to be complete

### Notation Consistency
- Check that notation is consistent across the entire paper, not just within sections
- Flag when the same symbol is reused with different meanings
- Suggest a notation table in the appendix if notation is complex

### Citation Verification
- For each major technical claim, verify that appropriate citations exist
- When searching for missing citations, use specific technical queries
- Prioritize seminal/foundational papers and recent relevant work
- Note if citations are missing from related work section versus method section

### Actionable Feedback
- Every issue should have a clear suggested fix
- Reference specific pages, equations, or figures when pointing out problems
- Provide before/after examples for presentation improvements
- Be specific about what readers might find confusing

## Example Citation Search Invocation

```bash
python BASE_DIR/scripts/paper_search.py \
  --query "variational autoencoder training stability" \
  --max-results 5 \
  --sort citations
```

This returns the 5 most-cited papers matching the query, which you can then assess for relevance.

---

**Last Updated:** 2026-03-03
**Version:** 1.0
