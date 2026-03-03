# Conference Review Formats

## NeurIPS

### Review Structure
- **Summary** (2-3 sentences): What does the paper do and what are its main contributions?
- **Strengths** (3-5 bullet points): Key positive aspects
- **Weaknesses** (3-5 bullet points): Key concerns
- **Questions for Authors**: Clarification questions
- **Limitations**: Did authors adequately address limitations?
- **Ethics Review Flag**: Any ethical concerns (data privacy, dual use, bias)
- **Overall Score**: 1-10 (1=strong reject, 5=borderline, 10=strong accept)
- **Confidence**: 1-5 (1=educated guess, 3=fairly confident, 5=absolutely certain)

### NeurIPS Checklist Items
- Do claims match theoretical/experimental evidence?
- Is reproducibility information sufficient (code, hyperparameters, compute)?
- Is code/data availability stated?
- Is broader impact discussed?
- Are limitations acknowledged?
- Are figures and tables clear and informative?
- Is the paper within scope of NeurIPS?

## ICML

### Review Structure
- **Summary**: Brief description of contributions
- **Strengths**: Major and minor strengths listed separately
- **Weaknesses**: Major and minor weaknesses listed separately
- **Clarity**: Is the paper well-written and well-organized?
- **Relation to Prior Work**: Adequately discussed? Position relative to related work clear?
- **Reproducibility**: Can results be reproduced? Sufficient implementation details?
- **Overall Score**: 1-10 (1=strong reject, 10=strong accept)
- **Confidence**: 1-5

### ICML-Specific Criteria
- Theoretical contributions must include proofs or proof sketches
- Experimental papers need error bars and multiple runs
- Position papers need comprehensive literature coverage
- Comparison with baselines must be fair (same computational budget, hyperparameter tuning)
- Statistical significance testing required for claims

## CVPR

### Review Structure
- **Summary**: Paper summary and main contributions
- **Strengths and Weaknesses**: Combined section with clear labeling of each point
- **Questions and Suggestions**: For author rebuttal and improvement
- **Missing References**: Papers that should be cited or compared against
- **Overall Score**: 1-6 (1=strong reject, 2=reject, 3=weak reject, 4=weak accept, 5=accept, 6=strong accept)
- **Confidence**: 1-3 (1=low, 2=medium, 3=expert)

### CVPR-Specific Criteria
- Visual results quality and diversity of test cases
- Comparison with state-of-the-art on standard benchmarks (multiple datasets)
- Ablation study completeness (all components justified)
- Real-world applicability and generalization discussed
- Runtime/computational efficiency analysis
- Figure quality and caption informativeness

## ACL

### Review Structure
- **Paper Summary**: What the paper does and its main contributions
- **Summary of Strengths**: Key positive aspects
- **Summary of Weaknesses**: Key concerns
- **Comments, Suggestions and Typos**: Detailed feedback by section
- **Missing References**: Important related work not cited
- **Questions for Authors**: Clarification needed for rebuttal
- **Soundness**: 1-4 (1=poor methodology, 4=excellent)
- **Presentation**: 1-4 (1=unclear writing, 4=very clear)
- **Originality**: 1-4 (1=not original, 4=highly novel)
- **Significance**: 1-4 (1=marginal impact, 4=major impact)
- **Overall Score**: 1-5 (1=poor, 2=weak, 3=acceptable, 4=good, 5=excellent)
- **Confidence**: 1-5

### ACL-Specific Criteria
- Linguistic soundness and theoretical grounding
- Dataset construction methodology and annotation agreement
- Multilingual considerations (if applicable)
- Ethical considerations for NLP applications (bias, toxicity, privacy)
- Reproducibility of experiments and datasets
- Human evaluation (inter-annotator agreement, adequate sample size)

## AAAI

### Review Structure
- **Summary**: Brief paper summary with main contributions
- **Strengths**: Key contributions and positive aspects
- **Weaknesses**: Key concerns and limitations
- **Questions**: Clarification questions for authors
- **Minor Issues**: Writing, clarity, presentation issues
- **Overall Assessment**: Accept/Reject recommendation with justification
- **Overall Score**: 1-10 (1=strong reject, 5=borderline, 10=strong accept)
- **Confidence**: 1-5

### AAAI-Specific Criteria
- Novelty relative to published work in the field
- Technical quality and correctness of approach
- Clarity of presentation and organization
- Significance of results and potential impact
- Adequacy of related work discussion
- Sufficiency of experimental evaluation

## ICCV

### Review Structure
- **Summary**: What the paper does
- **Strengths**: Positive aspects with detail
- **Weaknesses**: Concerns and limitations
- **Technical Issues**: Specific technical problems (if any)
- **Missing Experiments**: Experiments that would strengthen the work
- **Clarity Issues**: Presentation problems
- **Minor Issues**: Typos and small issues
- **Overall Score**: 1-6 (1=reject, 6=accept)
- **Confidence**: 1-3

### ICCV-Specific Criteria
- Novel approach to computer vision problems
- Comprehensive experimental validation on multiple datasets
- Comparison with recent state-of-the-art methods
- Ablation studies demonstrating importance of components
- Code and model availability for reproducibility
- Analysis of failure cases and limitations

## ICLR

### Review Structure
- **Summary**: Brief description of the paper and contributions
- **Strengths**: Positive aspects of the work
- **Weaknesses**: Concerns and limitations
- **Questions**: Questions for the authors
- **Minor Issues**: Small issues and suggestions
- **Soundness**: Technical correctness (1-5 scale)
- **Presentation Quality**: Clarity and organization (1-5 scale)
- **Originality**: Novelty of ideas (1-5 scale)
- **Significance**: Impact and importance (1-5 scale)
- **Overall Recommendation**: Accept/Borderline/Reject
- **Confidence**: 1-5

### ICLR-Specific Criteria
- Theoretical understanding and justification
- Comprehensive experimental evaluation
- Fair comparison with baselines
- Analysis of learned representations
- Discussion of computational requirements
- Clarity of method description and reproducibility

## Default (Generic)

Use this format when no specific conference is specified:

### Review Structure
- **Summary** (2-3 sentences): What the paper does and its main contributions
- **Strengths** (3-5 bullet points): Key positive aspects
- **Weaknesses** (3-5 bullet points): Key concerns
- **Major Issues** (numbered list): Significant problems with explanations and suggested fixes
- **Minor Issues** (numbered list): Small issues, typos, presentation problems
- **Questions for Authors**: Clarification questions and requests for additional information
- **Missing References**: Relevant work not cited (table format)
- **Overall Assessment**: Clear recommendation (Strong Accept / Accept / Weak Accept / Borderline / Weak Reject / Reject / Strong Reject)
- **Confidence**: Assessment of reviewer certainty (Low / Medium / High / Expert)

### Generic Evaluation Criteria
- Is the work novel and original?
- Is the technical approach sound?
- Are the experimental results convincing?
- Is the work clearly presented?
- Is the significance and impact clear?
- Are limitations and future work discussed?
- Is there sufficient detail for reproducibility?

## Severity Levels

### Lenient Review
- Focus on strengths first
- Frame weaknesses as suggestions for improvement
- Give benefit of the doubt on unclear points
- Acknowledge limitations without over-penalizing
- Score 1-2 points higher on overall assessment
- Use constructive, encouraging language
- Highlight potential rather than current state

### Standard Review
- Balanced assessment of strengths and weaknesses
- Typical conference reviewer tone
- Fair and objective scoring
- Point out issues but acknowledge merits
- Provide actionable feedback
- Consider community standards
- Score reflects typical conference bar

### Strict Review
- Rigorous evaluation against high standards
- Flag all issues including minor ones
- Demand strong evidence for every claim
- Detailed scrutiny of experimental design
- Careful comparison with related work
- Conservative scoring
- No benefit of the doubt on unclear points
- Score 1-2 points lower on overall assessment
- May use pointed language to emphasize issues

## Review Quality Checklist

All reviews should:
- [ ] Have specific examples and citations
- [ ] Provide actionable feedback
- [ ] Be respectful and professional
- [ ] Acknowledge merit even when recommending rejection
- [ ] Flag reviewer conflicts of interest
- [ ] Not make assumptions without evidence
- [ ] Be thorough but concise
- [ ] Follow the conference format guidelines
- [ ] Include confidence calibration
- [ ] Check for typos and clarity in the review itself
