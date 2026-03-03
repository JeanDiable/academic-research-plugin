---
name: paper-reviewing
description: >
  Conference-style academic paper peer review. Reads a paper PDF, assesses novelty,
  technical soundness, clarity, significance, reproducibility, and experimental design.
  Generates a structured review with summary, strengths, weaknesses, major/minor issues,
  questions, and scores. Supports NeurIPS, ICML, CVPR, ACL, AAAI, ICCV, ICLR formats
  with adjustable severity. Use when the user wants to "review a paper", "write a review",
  "assess this submission", "what are the weaknesses", or "generate a peer review".
user-invocable: true
argument-hint: "<pdf-path> [--conference NeurIPS|ICML|CVPR|ACL|AAAI|ICCV|ICLR] [--severity lenient|standard|strict]"
---

## Overview

Conduct a comprehensive conference-style peer review of an academic paper. This skill analyzes papers across six key dimensions:

1. **Novelty**: How original and innovative is the work?
2. **Technical Soundness**: Are the methods correct and well-justified?
3. **Clarity**: Is the paper well-written and organized?
4. **Significance**: How impactful is this work?
5. **Reproducibility**: Can others reproduce the results?
6. **Experimental Design**: Are experiments properly designed and comprehensive?

The review follows the format and checklist of a specified conference (NeurIPS, ICML, CVPR, ACL, AAAI, ICCV, ICLR) or a generic academic format. Severity can be adjusted (lenient, standard, strict) to calibrate tone and scoring standards.

## Arguments

### `<pdf-path>` (required)
Path to the paper PDF file to review. Can be absolute or relative path.

### `--conference` (optional)
Target conference to match review format. Options:
- `NeurIPS` - Neural Information Processing Systems
- `ICML` - International Conference on Machine Learning
- `CVPR` - IEEE/CVF Conference on Computer Vision and Pattern Recognition
- `ACL` - Association for Computational Linguistics
- `AAAI` - Association for the Advancement of Artificial Intelligence
- `ICCV` - IEEE/CVF International Conference on Computer Vision
- `ICLR` - International Conference on Learning Representations
- If omitted, uses generic academic format

### `--severity` (optional, default: standard)
Tone and scoring calibration:
- `lenient` - Focus on strengths, constructive framing, generous scoring
- `standard` - Balanced assessment, typical conference reviewer tone
- `strict` - Rigorous evaluation, all issues flagged, conservative scoring

## Setup

Install dependencies:
```bash
python -m pip install -r "BASE_DIR/scripts/requirements.txt"
```

Required packages:
- `PyPDF2` or `pdfplumber` - PDF parsing and text extraction
- `requests` - HTTP requests for arXiv and paper searches
- `python-dateutil` - Date handling

## Workflow

### Step 1: Extract and Analyze Paper Content

Read the entire PDF using the Read tool. For papers exceeding 20 pages, paginate the reading:
- Pages 1-20 for first batch
- Pages 21-40 for second batch
- Continue in 20-page increments

While reading, compile comprehensive notes:
- **Title, Authors, Affiliation**: Record metadata
- **Abstract**: Core claims and contributions
- **Introduction**: Problem statement and motivation
- **Related Work**: How authors position their work
- **Main Technical Contribution**: Core methodology and novelty
- **Experimental Setup**: Datasets, baselines, metrics
- **Results and Analysis**: Key findings and ablations
- **Discussion and Limitations**: Author-acknowledged limitations
- **Reproducibility Information**: Code availability, hyperparameters, compute requirements

### Step 2: Assess Six Core Dimensions

For each dimension, write 2-3 sentences providing specific analysis:

**Novelty**: Is this genuinely new? What distinguishes it from prior work? Are the ideas incremental or transformative? Does it advance the field in a meaningful way?

**Technical Soundness**: Are mathematical proofs correct (if present)? Are assumptions justified? Are there logical gaps or unjustified leaps? Do the experiments actually validate the claims? Are there potential flaws in methodology?

**Clarity**: Is the writing clear and well-organized? Are key concepts explained before use? Are figures and tables informative with good captions? Is the main contribution easy to identify? Are mathematical notations consistent?

**Significance**: Would this work change how people think about the problem? How many researchers/practitioners would benefit? What is the potential real-world impact? Does it open new research directions?

**Reproducibility**: Is there sufficient implementation detail to reproduce results? Is code promised or available? Are hyperparameters and training procedures documented? Are computational requirements specified? Can someone independent reproduce the main results?

**Experimental Design**: Are baselines appropriate and state-of-the-art? Are comparisons fair (same hyperparameter tuning, computational budget)? Are ablations sufficient to understand component contributions? Are error bars/confidence intervals reported? Is evaluation on multiple datasets? Are failure cases discussed?

### Step 3: Search for Missing Related Work

Extract 3-5 key technical concepts or method names from the paper. For each concept, execute:

```bash
python "BASE_DIR/scripts/paper_search.py" \
  --query "[concept name or method]" \
  --max-results 10 \
  --sort citations
```

Identify papers that are highly relevant (by citation count, recency, or topical alignment) but NOT cited in the submission. Compile these into a "Missing References" section.

### Step 4: Generate Structured Review

Use the conference format from `references/conference_formats.md` corresponding to `--conference` argument. If no conference specified, use the Default (Generic) format.

For specified conferences, follow their exact structure:
- **NeurIPS**: Summary, Strengths, Weaknesses, Questions, Limitations, Ethics Flag, Score (1-10), Confidence (1-5)
- **ICML**: Summary, Major/Minor Strengths, Major/Minor Weaknesses, Clarity, Prior Work, Reproducibility, Score (1-10), Confidence (1-5)
- **CVPR**: Summary, Strengths & Weaknesses, Questions, Missing References, Score (1-6), Confidence (1-3)
- **ACL**: Summary, Strengths, Weaknesses, Comments, Missing References, Soundness/Presentation/Originality/Significance (1-4), Overall (1-5), Confidence (1-5)
- **AAAI**: Summary, Strengths, Weaknesses, Questions, Assessment, Score (1-10), Confidence (1-5)
- **ICCV**: Summary, Strengths, Weaknesses, Technical Issues, Missing Experiments, Clarity Issues, Minor Issues, Score (1-6), Confidence (1-3)
- **ICLR**: Summary, Strengths, Weaknesses, Questions, Minor Issues, Soundness/Presentation/Originality/Significance (1-5), Recommendation, Confidence (1-5)

All reviews include conference-specific checklist items from the reference file.

### Step 5: Calibrate Tone per Severity

Adjust language, framing, and scoring based on severity argument:

**Lenient**:
- Lead with strengths and innovations
- Frame each weakness as "opportunity for improvement" or "could be strengthened by"
- Interpret unclear points charitably
- Acknowledge limitations without penalizing heavily
- Increase overall scores by 1-2 points from neutral assessment
- Use encouraging, supportive language
- Emphasize potential and merit

**Standard**:
- Balance strengths and weaknesses equally
- Use typical peer reviewer tone (professional, critical but fair)
- Acknowledge merits even when recommending improvements
- Score reflects average conference acceptance bar
- Direct but respectful language
- Fair representation of both positive and negative aspects

**Strict**:
- Begin with weaknesses and concerns
- Flag all issues including minor presentation problems
- Demand explicit evidence for all claims
- Scrutinize experimental methodology carefully
- Compare rigorously against related work
- Decrease overall scores by 1-2 points from neutral assessment
- Use pointed language to emphasize significance of issues
- No benefit of doubt on ambiguous points

### Step 6: Format and Output

Generate final review following conference template. Include:

1. Complete review text in markdown format
2. Structured scoring section with all numerical and categorical ratings
3. Conference-specific checklist items (if applicable)
4. JSON file with missing references search results
5. Metadata: review date, conference, paper title, severity level

## Output Format

The review structure (when no conference specified):

```markdown
# Paper Review: <Paper Title>

## Summary
[2-3 sentence summary of what the paper does and its main contributions]

## Strengths
1. [First strength with specific example or evidence]
2. [Second strength with explanation]
3. [Additional strengths as applicable]

## Weaknesses
1. [First weakness with specific example]
2. [Second weakness with explanation]
3. [Additional weaknesses as applicable]

## Major Issues
1. **[Issue Title]**: [Detailed explanation of the problem]
   → Suggested fix: [Specific actionable suggestion]

2. **[Issue Title]**: [Detailed explanation]
   → Suggested fix: [Specific actionable suggestion]

[Continue for all major issues]

## Minor Issues
1. [Minor issue or suggestion with line/section reference]
2. [Typo or presentation issue]
3. [Additional minor items]

## Questions for Authors
1. [Specific question about methodology, results, or claims]
2. [Clarification requested about experimental setup]
3. [Request for additional analysis or results]

## Missing Related Work

| Paper Title | Key Contribution | Relevance | Should Be Cited In Section |
|------------|-----------------|-----------|---------------------------|
| [Title 1] | [Brief description] | [Why relevant to submission] | [Where in paper] |
| [Title 2] | [Brief description] | [Why relevant to submission] | [Where in paper] |

## Scores

- **Overall Assessment**: [Strong Accept / Accept / Weak Accept / Borderline / Weak Reject / Reject / Strong Reject]
- **Overall Score**: X/10 (or 1-6 for CVPR, etc.)
- **Confidence**: Low / Medium / High / Expert (1-5 scale)
- **Novelty**: Low / Medium / High
- **Technical Soundness**: Low / Medium / High
- **Significance**: Low / Medium / High
- **Clarity**: Low / Medium / High

## Additional Notes
[Any final comments about significance, presentation, or specific feedback]
```

For conference-specific formats, structure follows the exact template from `references/conference_formats.md` with appropriate section names and scoring scales.

## Output Directory Structure

Reviews are saved to: `./output/paper-reviewing/YYYY-MM-DD-HHMMSS/`

Directory contents:
- **review.md** - Complete review in markdown format
- **metadata.json** - Metadata including:
  - Paper title and authors
  - Review date and time
  - Conference format used
  - Severity level applied
  - Reviewer notes
- **missing_references.json** - Search results for potentially missing citations:
  ```json
  {
    "search_queries": ["concept1", "concept2", ...],
    "results": [
      {
        "query": "concept name",
        "papers": [
          {
            "title": "Paper Title",
            "authors": "Author1, Author2",
            "year": 2024,
            "citations": 150,
            "relevance_reason": "Why this is relevant"
          }
        ]
      }
    ]
  }
  ```

## Usage Examples

```bash
# Review a paper with NeurIPS format and standard severity
paper-reviewing /path/to/paper.pdf --conference NeurIPS

# Review with strict tone and CVPR format
paper-reviewing paper.pdf --conference CVPR --severity strict

# Lenient review with generic format
paper-reviewing paper.pdf --severity lenient

# Default: generic format, standard severity
paper-reviewing paper.pdf
```

## Best Practices

1. **Be Specific**: Always reference specific sections, figures, or claims
2. **Be Constructive**: Frame criticism as actionable improvement suggestions
3. **Be Evidence-Based**: Support all assessments with evidence from the paper
4. **Be Fair**: Acknowledge merit even when recommending rejection
5. **Be Thorough**: Cover all six dimensions; don't focus only on novelty
6. **Be Professional**: Maintain respectful tone even in strict mode
7. **Be Clear**: Write review clearly so authors can understand and respond
8. **Be Timely**: Complete reviews promptly to respect deadlines
9. **Flag Conflicts**: Note any potential reviewer bias or conflicts of interest
10. **Check Reproducibility**: Verify code/data availability and documentation claims

## Limitations

- Requires PDF in readable text format (scanned PDFs need OCR)
- Cannot verify all experimental claims without running code
- Novelty assessment depends on reviewer's knowledge of field
- Some domain-specific expertise may be needed for specialized fields
- Confidence scores reflect analysis, not ground truth correctness

## Conference-Specific Notes

### NeurIPS
- Emphasize broader impact and ethical considerations
- Check for reproducibility information extensively
- Verify code/data availability statements

### ICML
- Require theoretical proofs or proof sketches
- Demand rigorous experimental methodology
- Check statistical significance testing

### CVPR
- Assess visual results quality and diversity
- Require ablation studies
- Compare on standard benchmarks (COCO, ImageNet, etc.)

### ACL
- Consider linguistic and linguistic-methodological soundness
- Evaluate dataset quality and annotation agreement
- Flag ethical concerns in NLP applications

### AAAI
- Focus on novelty relative to published work
- Assess breadth of experimental evaluation
- Consider applicability and practical impact

### ICCV
- Emphasize visual quality and comprehensiveness
- Require multiple dataset evaluation
- Flag missing failure case analysis

### ICLR
- Demand theoretical understanding alongside experiments
- Check computational efficiency analysis
- Verify fair baseline comparisons

## Related Skills

- `paper-summarizing` - Generate concise paper summaries
- `literature-survey` - Build comprehensive literature surveys
- `experiment-analyzer` - Analyze experimental results and methodology
