---
name: paper-to-presentation
description: Convert sourced academic PDFs into a validated, editable PowerPoint deck through a Codex-compatible four-stage workflow using Python/PyMuPDF, Pillow, and Node.js/PptxGenJS.
---

# Paper-to-Presentation

Use this skill when a user asks Codex to turn academic papers, course readings, research PDFs, or a literature set into presentation materials or an editable PPTX. Do not use it for pitch decks, unsupported web summaries, or unsourced slide creation.

## Inputs and outputs

- Input PDFs: `papers/*.pdf`.
- Extracted figures and source indexes: `assets/` and `assets/figures/`.
- Narrative artifacts and slide specifications: `prd/`.
- Final deliverables: `output/final_presentation.pptx` and `output/speaker_notes.md`.
- Presentation settings: start from `references/sample_config.json`; copy it to `prd/presentation_config.json` before customization.

## Required environment

Install Python and Node dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
npm install
```

The workflow intentionally replaces Claude-specific `pdf`, `ppt-creator`, and `pptx` assumptions with executable tools that run in Codex cloud environments:

- Python + PyMuPDF extracts PDF text, images, page references, and figure metadata.
- Pillow validates image dimensions, aspect ratios, and readability risk.
- Node.js + PptxGenJS creates editable `.pptx` files.

## Workflow stages

Run the stages in order. Inspect each intermediate artifact before continuing.

### 1. Figure extraction

```bash
python .agents/skills/paper-to-presentation/scripts/extract_figures.py --papers papers --out assets
```

Outputs:

- `assets/figures/` with extracted images named by paper/page/object.
- `assets/figures_index.md` with paper, page, dimensions, caption context, visual/readability metadata, and suggested use.
- `assets/source_index.md` initialized with PDF inventory metadata.

Validation rules:

- Do not alter figure content.
- Discard tiny decorative images by default.
- Preserve page and paper provenance for every image.
- If a useful figure is embedded as vector content and cannot be extracted as an image, note the page in `figures_index.md` for manual screenshot extraction rather than inventing a replacement.

### 2. Text and evidence curation

```bash
python .agents/skills/paper-to-presentation/scripts/curate_text.py --papers papers --out assets
```

Outputs:

- `assets/core_text.md` with candidate sourced claims organized by paper.
- `assets/data_points.md` with candidate numeric results and comparison sentences.
- `assets/source_index.md` updated with page-level text snippets and provenance IDs.

Validation rules:

- Every claim must include paper filename and page number.
- Prefer author-stated findings, abstracts, conclusion sentences, method descriptions, and quantitative result sentences.
- Keep original technical terms when needed.
- Mark ambiguous or missing evidence instead of filling gaps from memory.

### 3. Narrative and slide specification generation

```bash
python .agents/skills/paper-to-presentation/scripts/generate_slide_specs.py --assets assets --prd prd --config .agents/skills/paper-to-presentation/references/sample_config.json
```

Outputs:

- `prd/slide_outline.md` with overall arc and timing.
- `prd/slide_specs.md` with one editable section per slide: assertion headline, layout, bullets, evidence, figure reference, provenance, and notes outline.
- `prd/source_map.md` mapping slides to source papers/pages.

Validation rules:

- Headlines must be full assertion sentences, not topic labels.
- Slides should keep surface text under 70 words.
- Figure references must point to files in `assets/figures/` and include a `[VERIFY]` line based on available figure metadata or direct image inspection.
- Do not write claims that are absent from `assets/core_text.md`, `assets/data_points.md`, or the original papers.

### 4. Editable PPTX generation

```bash
node .agents/skills/paper-to-presentation/scripts/generate_pptx.js --config prd/presentation_config.json --spec prd/slide_specs.md --out output/final_presentation.pptx
```

Outputs:

- `output/final_presentation.pptx`.
- `output/speaker_notes.md`.

Validation rules:

- Use PptxGenJS shapes/text/images so slides remain editable.
- Put provenance in speaker notes, not on the slide surface.
- Before placing figures, run `validate_assets.py` or equivalent Pillow checks for dimensions and readability risk.
- If a figure appears mismatched or unreadable, switch to text-only or split into a figure-focused slide; never force an illegible figure into a dense slide.

## Limitations

- Automated extraction cannot reliably recover all vector-only figures, multi-panel figure semantics, or table structure from every PDF.
- The scripts generate a conservative draft specification; Codex must review provenance and narrative quality before final PPTX generation.
- OCR is not included. Scanned PDFs require an OCR preprocessing step before this skill can curate text.
- The workflow does not generate a real presentation unless the user explicitly asks to proceed after intermediate artifacts are created and validated.
