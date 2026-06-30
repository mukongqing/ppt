# Paper-to-Presentation

A reusable Codex-compatible skill that transforms academic papers into a sourced, editable PowerPoint workflow. The pipeline preserves the original four-stage design—figure extraction → text and evidence curation → narrative/slide specification → PPTX generation—without relying on Claude-specific `pdf`, `ppt-creator`, or `pptx` skills.

## Codex skill location

The repository-scoped skill lives at:

```text
.agents/skills/paper-to-presentation/
```

Codex should read `.agents/skills/paper-to-presentation/SKILL.md` before any paper-to-PPT task in this repository.

## Repository layout

```text
papers/                         # Input PDFs supplied by the user
assets/                         # Extracted figures, source indexes, evidence files
assets/figures/                 # Extracted figure images
prd/                            # Slide outline, slide specs, source map, copied config
output/                         # Final editable PPTX and speaker notes
.agents/skills/paper-to-presentation/
  SKILL.md                      # Codex skill instructions and workflow contract
  scripts/                      # Runnable Python and Node.js implementation files
  references/sample_config.json # Minimal presentation configuration
```

## Required environment setup

From the repository root, install the runtime dependencies:

```bash
python -m pip install -r requirements.txt
npm install
```

The workflow uses:

- **Python + PyMuPDF** for PDF page text and embedded figure extraction.
- **Pillow** for image dimension and readability checks.
- **Node.js + PptxGenJS** for editable PowerPoint generation.

## Place papers in `papers/`

Copy academic PDFs into the repository-level `papers/` directory:

```bash
mkdir -p papers
cp /path/to/paper-1.pdf papers/
cp /path/to/paper-2.pdf papers/
```

Do not place generated intermediate files in `papers/`; keep generated artifacts in `assets/`, `prd/`, and `output/`.

## Run the workflow stages

Run stages in order and inspect each intermediate artifact before proceeding. The scripts are conservative helpers: they produce sourced drafts and indexes that Codex or a human should review before generating a final deck.

### Stage 1 — figure extraction

```bash
python .agents/skills/paper-to-presentation/scripts/extract_figures.py --papers papers --out assets
```

Outputs:

- `assets/figures/`
- `assets/figures_index.md`
- `assets/source_index.md`

### Stage 2 — text and evidence curation

```bash
python .agents/skills/paper-to-presentation/scripts/curate_text.py --papers papers --out assets
```

Outputs:

- `assets/core_text.md`
- `assets/data_points.md`
- updated `assets/source_index.md`

### Stage 3 — narrative and slide specification generation

```bash
python .agents/skills/paper-to-presentation/scripts/generate_slide_specs.py --assets assets --prd prd --config .agents/skills/paper-to-presentation/references/sample_config.json
```

Outputs:

- `prd/slide_outline.md`
- `prd/slide_specs.md`
- `prd/source_map.md`
- `prd/presentation_config.json`

Review these files for provenance, narrative flow, unsupported claims, and figure matches before generating a deck.

### Optional validation — figure readability checks

```bash
python .agents/skills/paper-to-presentation/scripts/validate_assets.py --figures assets/figures
```

Output:

- `assets/figure_validation.md`

### Stage 4 — generate the final editable PPTX

Only run this after the intermediate artifacts are generated and reviewed:

```bash
node .agents/skills/paper-to-presentation/scripts/generate_pptx.js --config prd/presentation_config.json --spec prd/slide_specs.md --out output/final_presentation.pptx
```

Outputs:

- `output/final_presentation.pptx`
- `output/speaker_notes.md`

## Using the skill later

- **Codex CLI:** open this repository and ask Codex to use the `paper-to-presentation` skill. Codex should read `.agents/skills/paper-to-presentation/SKILL.md`, place/read PDFs from `papers/`, then run the staged scripts.
- **Codex IDE extension:** keep the repository workspace open, add PDFs to `papers/`, and request a paper-to-PPT workflow. The root `AGENTS.md` instructs Codex to preserve provenance and generate intermediate artifacts before PPTX output.
- **Codex App:** attach or add PDFs into `papers/` in the workspace, then ask for a sourced presentation. Review `assets/` and `prd/` artifacts before approving final deck generation.

## Constraints

| Dimension | Rule |
|-----------|------|
| Content provenance | Every claim, figure, table, and numeric result must trace to a source PDF. |
| Fabrication | Missing evidence must be marked as missing; never invent citations or findings. |
| Slide text | Keep surface text concise, ideally no more than 70 words per slide. |
| Citations | Put provenance in speaker notes and PRD artifacts, not on slide surfaces. |
| Output | Generate editable PowerPoint via PptxGenJS, not screenshots of slides. |

## Not generated yet

This repository implements, tests, and documents the workflow. It does not include a generated real presentation; add PDFs to `papers/` and run the staged commands when you are ready to create one.

## License

MIT
