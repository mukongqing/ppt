#!/usr/bin/env python3
"""Create conservative draft outline/spec files from curated artifacts."""
from __future__ import annotations
import argparse, json, re, shutil
from pathlib import Path

def bullets(lines, n=3):
    items = [re.sub(r'^-\s*', '', l).strip() for l in lines if l.startswith('- ')]
    return items[:n] or ['Evidence pending review from curated text.']

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--assets', default='assets'); ap.add_argument('--prd', default='prd'); ap.add_argument('--config', default='.agents/skills/paper-to-presentation/references/sample_config.json')
    args = ap.parse_args(); assets = Path(args.assets); prd = Path(args.prd); prd.mkdir(exist_ok=True)
    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    shutil.copyfile(args.config, prd / 'presentation_config.json')
    core_lines = (assets / 'core_text.md').read_text(encoding='utf-8').splitlines() if (assets / 'core_text.md').exists() else []
    fig_lines = [l for l in (assets / 'figures_index.md').read_text(encoding='utf-8').splitlines()[2:]] if (assets / 'figures_index.md').exists() else []
    bs = bullets(core_lines, 9)
    outline = [f"# Slide outline: {cfg.get('title','Paper-to-Presentation Draft')}", '', f"Target: {cfg.get('talk_minutes',15)} minutes / {cfg.get('slide_count_target',12)} slides", '', '1. Establish the paper set and research problem.', '2. Summarize methods and evidence from sourced papers.', '3. Compare numeric findings and limitations.', '4. Close with sourced takeaways and open questions.']
    specs = [f"# Slide specifications: {cfg.get('title','Paper-to-Presentation Draft')}\n"]
    source_map = ['| Slide | Sources |', '|---:|---|']
    slide_defs = [('Cover', 'This deck summarizes the sourced paper set.'), ('Problem', 'The selected papers motivate a focused research problem.'), ('Evidence', 'The extracted evidence supports a concise technical narrative.'), ('Takeaways', 'The final takeaways remain bounded by the cited papers.')]
    for i, (kind, headline) in enumerate(slide_defs, 1):
        fig_ref = ''
        verify = '[VERIFY] Text-only slide; no figure referenced.'
        if kind == 'Evidence' and fig_lines:
            fig_ref = fig_lines[0].split('|')[1].strip()
            verify = f'[VERIFY] Slide {i}: Figure metadata exists for {fig_ref}; visually inspect before final use.'
        slide_bullets = bs[(i-1)*2:i*2] or bs[:2]
        specs += [f'## Slide {i}: {headline}', f'- Layout: {"title" if i == 1 else "content"}', f'- Figure: {fig_ref or "none"}', '- Bullets:']
        specs += [f'  - {b}' for b in slide_bullets]
        specs += [f'- Provenance: derived from assets/core_text.md and assets/source_index.md', '- Speaker notes outline: hook → claim → evidence → transition.', verify, '']
        source_map.append(f'| {i} | assets/core_text.md; assets/source_index.md |')
    (prd / 'slide_outline.md').write_text('\n'.join(outline) + '\n', encoding='utf-8')
    (prd / 'slide_specs.md').write_text('\n'.join(specs), encoding='utf-8')
    (prd / 'source_map.md').write_text('\n'.join(source_map) + '\n', encoding='utf-8')
    print('Wrote prd/slide_outline.md, prd/slide_specs.md, prd/source_map.md, and prd/presentation_config.json')
    return 0
if __name__ == '__main__': raise SystemExit(main())
