---
name: poster-slides-maker
description: >
  Academic poster and presentation slides creator. Given a paper PDF or LaTeX project,
  generates conference-quality slides (reveal.js HTML) and/or a poster (single-page
  responsive HTML). Supports custom templates, configurable page count, and produces
  standalone files that can be opened in any browser and exported to PDF. Use when the
  user wants to "make slides", "create a presentation", "design a poster", "prepare
  for my talk", "make conference materials", or "create an oral presentation".
user-invocable: true
argument-hint: "<pdf-or-latex-path> [--type both] [--template template.html] [--pages 10]"
---

## Overview

The poster-slides-maker skill generates publication-quality presentation materials from academic papers. It produces standalone HTML files that work in any browser with no dependencies—all resources are loaded from CDN. The skill supports generating:

- **Slides** — Interactive reveal.js presentations with speaker notes, optimized for export to PDF
- **Poster** — Single-page responsive HTML poster with grid layout, suitable for printing at A0 or display on screen
- **Both** — Generate slides and poster in one command

All output files are self-contained and can be opened immediately in any modern browser (Chrome, Firefox, Safari, Edge).

## Arguments

**`<paper-path>`** (required)
Path to the source material: either a PDF file (`paper.pdf`) or a LaTeX project main file (`main.tex`).

**`--type`** (optional, default: `both`)
What to generate: `slides`, `poster`, or `both`.

**`--template`** (optional)
Path to a custom HTML template to match your desired style. If provided, the generated slides or poster will adopt the color scheme, fonts, and CSS patterns from this template.

**`--pages`** (optional, default: `10`)
Target number of slides. Used to scale the method and results sections. For example, `--pages 15` will expand the presentation with more detailed methodology and results breakdown.

## Workflow

The skill executes five sequential steps to transform raw academic content into polished presentation materials.

### Step 1: Extract Content

**From PDF input:**
- Read the PDF with pagination to handle large documents (pages 1-20, then 21-40, etc.)
- Extract text, identify section boundaries, and locate references

**From LaTeX input:**
- Read all `.tex` files in the project directory and subdirectories
- Parse the structure to identify: title, author list, affiliations, abstract, sections, subsections
- Identify all figure and table references

**Extract these key elements:**
- Paper title
- All author names
- Institutional affiliations for each author
- Abstract text
- Section structure and headings
- Key equations (preserve as displayed in the original)
- Main results: important numbers, benchmark scores, accuracy metrics
- Tables with experimental results
- Key citations (extract author + year + title)
- Conclusion and future work sections

**Note on figures:** While we cannot extract actual images from PDFs, we document all figure references and create placeholders or simple HTML/SVG diagrams as described in the "Figure Handling" section.

### Step 2: Design Information Hierarchy

**For slides** — map content to the target page count. Each slide must communicate one key message:

- **Slide 1** — Title slide: paper title, all authors, affiliations
- **Slide 2** — Motivation / Problem statement: "Why should the audience care?"
- **Slide 3** — Background / Related work: 3-4 most relevant prior approaches with brief explanation
- **Slides 4-6** — Methodology: Break into logical steps. Use text, equations, and simple diagrams (SVG or placeholder comments)
- **Slides 7-9** — Experiments / Results: Key tables and headline numbers. Show 3-4 most impactful results
- **Slide 10** — Conclusion + Future work + "Thank you" closing
- **Slide 11+** — References (if needed, use small font; or include citations inline in prior slide)

**Scaling by page count:** If `--pages` is greater than 10, insert additional detail slides in the Method section (e.g., 15 pages might use Slides 4-8 for method instead of 4-6). If less than 10, consolidate results or combine sections.

**For poster** — organize into a grid layout with sections:

- **Header banner** — Full width: title, authors, affiliations, institution logos (if available)
- **Abstract** — 150-200 words, clearly visible
- **Method** — Key steps with diagrams or flowcharts
- **Key Results** — Visual centerpiece: tables, important numbers, success metrics
- **Conclusion** — Main takeaway and future directions

**Design principles:**
- Maintain high contrast between text and background
- Use serif fonts for body text (Georgia, Times New Roman)
- Use sans-serif fonts only for accent headings if desired
- Keep whitespace generous to avoid clutter
- Ensure text is readable at arm's length for posters

### Step 3: Generate Slides HTML

1. Read the base template from `assets/reveal-template.html`
2. Replace template placeholders:
   - `{{TITLE}}` → extracted paper title
   - `{{AUTHORS}}` → "John Smith, Jane Doe"
   - `{{AFFILIATIONS}}` → "University of Example, Institution X"
3. For each content slide, create a `<section>` element:
   ```html
   <section>
       <h2>Methodology</h2>
       <ul>
           <li>Key point 1</li>
           <li>Key point 2</li>
       </ul>
       <div class="highlight-box">
           Main takeaway for this slide
       </div>
       <aside class="notes">
           Detailed speaker notes explaining each point...
       </aside>
   </section>
   ```
4. Add speaker notes in `<aside class="notes">` tags for each slide. These help the presenter remember talking points without displaying them to the audience.
5. Use template CSS classes:
   - `.highlight-box` — for the key takeaway or insight on each slide
   - `.small` — for reference citations or fine print
6. For mathematical equations: use KaTeX syntax (wrapped in `$$...$$`). The template loads the math plugin automatically.
7. For tables: use standard HTML `<table>` elements. The template applies professional styling with borders and alternating row backgrounds.
8. Keep text minimal — use bullet points, not full paragraphs. Aim for 3-5 bullet points per slide maximum.

### Step 4: Generate Poster HTML

Create a standalone HTML file with the following structure:

1. **HTML/CSS Grid layout:**
   - Use CSS Grid with 3 columns for A0 landscape orientation
   - Full-width header section for title and metadata
   - Main content grid with Method, Results, and Conclusion sections
   - Responsive design that adapts to smaller screens

2. **Sections and content:**
   ```html
   <header class="poster-header">
       <h1>{{TITLE}}</h1>
       <p class="poster-authors">{{AUTHORS}}</p>
       <p class="poster-affiliation">{{AFFILIATIONS}}</p>
   </header>
   <main class="poster-grid">
       <section class="poster-abstract"><!-- Abstract --></section>
       <section class="poster-method"><!-- Method --></section>
       <section class="poster-results"><!-- Key Results --></section>
       <section class="poster-conclusion"><!-- Conclusion --></section>
   </main>
   ```

3. **Print-optimized CSS:**
   - Include `@media print` rules for A0 paper size (landscape)
   - Set margins to 0 for full-bleed printing
   - Ensure text size is readable when printed (minimum 14-16pt for body text)
   - Prevent page breaks within sections using `page-break-inside: avoid`

4. **Academic styling:**
   - Serif fonts (Georgia, Times New Roman) for body text
   - Dark text on white background for contrast
   - Clean borders between sections
   - Minimal color accents (blues or grays if institution colors are not detected)
   - Professional spacing and alignment

5. **Responsive design:**
   - Media queries for tablet and mobile screens
   - Text scaling that maintains readability
   - Grid that collapses to single column on small screens
   - Posters should look good both on screen and in print

### Step 5: Handle Custom Templates

If `--template` is provided:

1. Read the custom template file
2. Extract its CSS styles, including:
   - Color scheme (primary, secondary, accent colors)
   - Font families and sizes
   - Spacing and padding patterns
   - Border styles and shadows
   - Background colors
3. Parse the HTML structure to understand layout patterns
4. Apply extracted styles to generated content instead of defaults
5. Preserve the custom template's overall aesthetic while inserting the academic content
6. Ensure the custom template includes or maintains:
   - Print-to-PDF support
   - Responsive design rules
   - Speaker notes support (for slides)

## Figure Handling

**Important limitation:** The skill cannot extract actual figures or images from PDF documents.

**For figure references, create one of these alternatives:**

1. **Simple SVG/HTML diagrams** — For methodology flowcharts, block diagrams, or process flows:
   - Create minimal SVG elements inline in the HTML
   - Use rectangles, arrows, and text annotations
   - Example: A simple flowchart showing algorithm steps

2. **HTML placeholder comments** — Clearly mark positions for figures:
   ```html
   <!-- INSERT FIGURE 1 HERE: System architecture diagram showing three main components:
        preprocessing (left), neural network model (center), post-processing (right) -->
   ```

3. **Reference the original** — Mention where to find the figure:
   - "See Figure 3 in the paper for the complete experimental setup"
   - "Refer to Figure 2 in the original publication for the full methodology flowchart"

4. **For tables with numerical results** — Recreate as HTML tables:
   - Extract all data from tables in the paper
   - Format as `<table>` elements with proper headers
   - Maintain column alignment and precision of numbers
   - Include table captions above the table

## Export Instructions

Include these export instructions as HTML comments in the generated files:

**For slides.html:**
```
<!-- EXPORT INSTRUCTIONS:
To export slides as PDF with speaker notes:
1. Open this file in Google Chrome
2. Press Ctrl+P (Windows) or Cmd+P (Mac) to open Print dialog
3. In the print settings:
   - Make sure "Background graphics" is checked
   - Set margins to None
   - Change destination to "Save as PDF"
   - Click Save

To view speaker notes during presentation:
1. Append "?print-pdf" to the URL in the address bar
2. Or press 'S' key during slideshow to open speaker view
3. Press 'P' to start presenter mode with notes visible
-->
```

**For poster.html:**
```
<!-- EXPORT INSTRUCTIONS FOR POSTER:
To export poster as PDF at A0 size:
1. Open this file in Google Chrome
2. Press Ctrl+P (Windows) or Cmd+P (Mac) to open Print dialog
3. In the print settings:
   - Set Paper size: A0 (landscape)
   - Set Margins: None
   - Ensure "Background graphics" is checked
   - Change destination to "Save as PDF"
   - Click Save

Alternative A1 or A2 sizes: Change paper size in step 3

To print poster at actual size at a print shop:
1. Export as PDF (steps above)
2. Provide the PDF to your print shop
3. Request "No scaling" printing at A0 landscape
-->
```

## Output Directory

All generated files are placed in: `./output/poster-slides-maker/YYYY-MM-DD-HHMMSS/`

**Generated files:**

- **`slides.html`** — Full reveal.js presentation (generated if `--type slides` or `both`)
  - Self-contained, no external dependencies (all from CDN)
  - Includes speaker notes
  - Print-to-PDF ready
  - Keyboard navigation: arrow keys, space bar, S for speaker view

- **`poster.html`** — Standalone responsive poster (generated if `--type poster` or `both`)
  - Self-contained HTML with embedded CSS
  - Responsive layout for screen and print
  - A0 landscape optimized
  - No external dependencies

- **`README.md`** — Brief reference guide with:
  - How to export to PDF
  - How to customize colors and fonts
  - Keyboard shortcuts for slides
  - Tips for presenting
  - Links to slide and poster files

## Tips

**For optimal slide presentations:**
- Less text per slide is always better — aim for maximum 5 bullet points per slide
- Use the `.highlight-box` class to emphasize the "key takeaway" on each slide
- Put detailed explanations in speaker notes, not on the slide
- Keep equations minimal and use them to explain, not to decorate
- When showing results, highlight the number that matters most

**For poster design:**
- Make the "Key Results" section the visual centerpiece — readers should see this first
- Use tables for quantitative results, short text for qualitative insights
- Keep the abstract concise but complete (should answer: What was done? Why? What was found?)
- If the paper has many results, select the 3-4 most impactful for the poster
- Use whitespace generously — posters crowded with text are hard to read from a distance

**For custom templates:**
- If you have a brand template, provide it with `--template`
- The skill will extract and apply your color scheme and fonts
- Ensure your template includes basic structure (no need to be full — just CSS and layout hints)

**For LaTeX projects:**
- The skill will search for `\documentclass`, `\title`, `\author` commands
- If using BibTeX, citations will be extracted from the `.bib` files
- Included graphics paths will be noted (figures cannot be extracted but will be logged)

**For managing long papers:**
- Papers with 20+ pages are common; the skill extracts only the most important content
- Use `--pages` to control detail level
- For a 30-page paper, `--pages 20` will create a comprehensive presentation; `--pages 8` will focus on main contributions
