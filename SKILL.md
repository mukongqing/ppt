---
name: paper-to-presentation
description: Use when creating course presentation slides from academic papers. Triggers on: "做 pre", "课程汇报", "论文 PPT", "presentation from papers", "把论文做成 PPT", or any request to turn research papers into slides for an academic talk.
---

# Paper-to-Presentation

A four-stage pipeline that transforms N academic papers into a course presentation deck. Each stage is an independent agent task whose output feeds the next. Must execute sequentially.

## Invariants (enforced across all stages)

### Content
- Every claim traces to a specific paper. No fabrication. No extrapolation.
- Numerical results cite exact source: `[Paper X, Page N / Paragraph N]`
- Source annotations go in Speaker Notes, never on the slide surface.
- Assumed audience: undergraduate STEM students who have taken the relevant introductory course. Skip basic terminology. Avoid derivations.

### Visual
- Color palette: Ocean Gradient only—`#065A82` (deep blue) / `#1C7293` (teal) / `#21295C` (midnight) + `#FFFFFF` (white) + `#F2F2F2` (light gray)
- Dark backgrounds reserved for: cover, closing slide, chapter dividers.
- No animations. No transitions. No gradients. No decorative elements.
- Typography: system UI fonts for body, monospace for data.
- Margins: ≥ 48px horizontal, ≥ 36px vertical.

### Narrative
- Every slide headline is a complete assertion (not a topic label). Example: "EDT achieves 5× frame rate gain with comparable image quality"—not "EDT Method Overview".
- 3–5 supporting points + 1 piece of evidence (figure / table / data) per slide.
- Speaker notes: 45–60 seconds of spoken material per slide. Structure: hook → core claim → evidence explanation → transition.
- ≤ 70 words per slide (excluding annotations).

## Directory Convention

```
project/
  papers/           # Input: N PDF papers
  assets/figures/   # agent1 output: extracted figures
  assets/           # agent2 output: text materials + provenance tables
  prd/              # agent3 output: per-slide specifications
  final_presentation.pptx  # agent4 deliverable
```

## Pipeline Stages

### agent1 — Figure Extraction
- **Tool**: `pdf` skill
- **Task**: Extract all embedded figures (diagrams, data plots, tables) from N papers. Discard decorative icons < 100px.
- **Output**:
  - `assets/figures/` — image files, naming convention `P<N>_<descriptor>.png`
  - `assets/figures_index.md` — inventory table: `| Figure | Paper N | Page | Section | Visual description | Suggested use |`
    - **Section**: chapter/section where the figure appears in the paper (e.g. `§2.3 Method / Network Architecture`). Prevents Introduction diagrams from being used as method illustrations.
    - **Visual description**: one sentence describing what is literally visible in the figure (e.g. "block diagram: 3 encoder blocks → bottleneck → 3 decoder blocks, skip connections as dashed lines"). Describe content, not meaning. This is the anchor for agent3's matching.
- **Constraints**: Preserve ≥ 150 dpi equivalent. No re-compression. No content alteration.

### agent2 — Text Curation
- **Tool**: `pdf` skill
- **Task**: Extract conclusive statements, quantitative results, and course-material connection points from N papers. Tag every item with precise provenance.
- **Output**:
  - `assets/core_text.md` — curated claims organized by chapter: `- [Paper X, Page N / §N] Original claim summary (retain English terminology)`
  - `assets/source_index.md` — full provenance table: `| ID | Paper | Page/§ | Summary | Suggested use |`
  - `assets/data_points.md` — key metrics quick-reference (performance numbers, comparison tables)
- **Constraints**: Every row must be traceable to a paper passage. Retain original English technical terms. Strip derivations and verbose experimental protocols.

### agent3 — PRD Per-Slide Specification
- **Tool**: `ppt-creator` skill
- **Task**: Using agent1+agent2 outputs, apply pyramid principle to produce a detailed per-slide spec.
- **Output**:
  - `prd/slide_outline.md` — overall structure + timing allocation (~15–18 slides)
  - `prd/slide_specs.md` — per-slide spec table, 10 fields per slide: page / chapter / assertion headline / core claim / supporting points (3–5) / figure reference / provenance / speaker notes outline / suggested layout
  - `prd/source_map.md` — slide-to-paper provenance mapping
- **Constraints**: ppt-creator must not fabricate data. No business-pitch tone. Fit within 20 minutes.
- **Visual Verification Gate** (MANDATORY, before finalizing slide_specs.md):
  1. For every slide that references a figure, use the `Read` tool to open the actual image file.
  2. Write a verification line: `[VERIFY] Slide N: Saw [specific visible content], matches assertion "[headline]" because [reason].`
  3. If the figure does NOT match the slide assertion:
     - Swap in a better figure from `figures_index.md` and re-verify, OR
     - Mark slide layout as `text-only`, demote figure reference to speaker notes.
  4. Append all verification lines to `slide_specs.md` so agent4 has the evidence trail.

### agent4 — PPTX Generation
- **Tool**: `pptx` skill → `pptxgenjs`
- **Task**: Consume all outputs from agents 1–3. Generate slides page by page. Apply Ocean Gradient palette.
- **Output**: `final_presentation.pptx` + `speaker_notes.md`
- **Slide templates**: Cover (`#21295C` full-bleed) / TOC (white) / Standard content (top title bar + bottom page number) / Full-image / Closing (`#21295C` full-bleed)
- **Constraints**: Use relative paths for assets. Embed provenance in speaker notes on every slide. Use only fonts available on Windows.
- **Keyword Overlap Guardrail**: Before placing a figure on a slide:
  1. Extract keywords from: slide assertion headline + 3–5 supporting points
  2. Extract keywords from: figure filename + agent1 Visual description
  3. Filter stop words: the, a, an, of, in, on, and, with, using, for, from, this, that, these, those
  4. If zero overlap of meaningful keywords → skip figure, use text-only layout for that slot, append to speaker notes: `⚠ FIGURE-MISMATCH: [filename] skipped — no keyword overlap with slide content. Check manually.`
- **Layout Collision Detection** (MANDATORY for any slide with images):
  1. Before placing or resizing any image, read ALL existing shapes on the slide — record their (x, y, w, h) in inches.
  2. Run bounding-box overlap check: for every new or resized image, verify it does not intersect any text block's bounding box. Include a 0.15" safety margin around text blocks.
  3. Pay special attention to bottom-aligned elements (page numbers, footers, stat callouts) — these are the most common collision victims.
- **Text Overflow Prevention**: When resizing a text box to make room for images:
  1. Estimate required height: count lines in the text content, multiply by line height at current font size (e.g. 14pt ≈ 0.19" per line).
  2. Set text box height ≥ estimated required height. Never set height below the estimate.
  3. If the required height doesn't fit between the image and the next element below, reduce font size or split content to speaker notes — do not let text overflow its bounding box.
- **Minimum Spacing**: Vertical gap ≥ 0.25" between any image bottom and the text block immediately below it. Gap ≥ 0.15" between adjacent text blocks. Gaps below 0.10" cause visual occlusion even when bounding boxes technically don't intersect.
- **Aspect-Ratio-Aware Image Sizing**: Before allocating space to images on a slide:
  1. Read actual image dimensions (PIL `Image.open` → `.size`).
  2. Text-dense figures (diagrams, flowcharts, architecture overviews) need larger display area. Give them ≥ 40% more width than data plots or photographs on the same slide.
  3. Never assign equal widths to images with significantly different aspect ratios without verifying the narrowest image is still readable.
- **One-Shot Layout for Complex Slides**: For slides with 3+ images or where image + text + stat callouts compete for space:
  1. Write out a dimension plan first — list every element with its target (x, y, w, h) in inches.
  2. Verify the plan against all the spacing/collision/overflow rules above.
  3. Apply all changes in a single edit pass. Do not iterate element-by-element — it causes cascading adjustments.

## Operational Notes

- **File locking**: Before editing an existing `.pptx` with python-pptx, ensure PowerPoint is closed. If `PermissionError` on save, save to a different filename and rename after closing PowerPoint.
- **Verification**: After any layout change, run a bounding-box overlap check on all slide shapes (excluding header at y < 0.9" and footer at y > 4.9"). Report every overlap found before declaring success.

## Getting Started

1. Create a project directory and place paper PDFs in `papers/`.
2. Optionally, use `paper-search` CLI to collect papers first.
3. Execute agent1 → agent2 → agent3 → agent4 in strict order.
4. Verify each agent's output before proceeding to the next.
