#!/usr/bin/env python3
"""Extract embedded PDF images and build a sourced figure index."""
from __future__ import annotations
import argparse, hashlib, os
from pathlib import Path
import fitz
from PIL import Image, ImageFilter, ImageStat


def slug(name: str) -> str:
    return ''.join(c if c.isalnum() else '_' for c in name).strip('_')[:60]


def image_stats(path: Path) -> tuple[int, int, float]:
    with Image.open(path) as img:
        w, h = img.size
        gray = img.convert('L')
        edge_density = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0]
        return w, h, edge_density


def nearby_text(page: fitz.Page) -> str:
    text = page.get_text('text').replace('\n', ' ')
    for marker in ('Figure', 'Fig.', 'FIGURE', 'Table'):
        idx = text.find(marker)
        if idx >= 0:
            return text[idx:idx + 260].strip()
    return text[:220].strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--papers', default='papers')
    ap.add_argument('--out', default='assets')
    ap.add_argument('--min-width', type=int, default=100)
    ap.add_argument('--min-height', type=int, default=100)
    args = ap.parse_args()
    papers = sorted(Path(args.papers).glob('*.pdf'))
    out = Path(args.out); fig_dir = out / 'figures'
    fig_dir.mkdir(parents=True, exist_ok=True)
    out.mkdir(exist_ok=True)

    rows = ['| Figure | Paper | Page | Size | Edge density | Caption/context | Visual description | Suggested use |', '|---|---|---:|---:|---:|---|---|---|']
    sources = ['| ID | Paper | Pages | Notes |', '|---|---|---:|---|']
    seen: set[str] = set()
    for pidx, pdf in enumerate(papers, 1):
        doc = fitz.open(pdf)
        sources.append(f'| P{pidx} | {pdf.name} | {doc.page_count} | Input PDF for extraction and curation |')
        for page_num, page in enumerate(doc, 1):
            context = nearby_text(page).replace('|', '\\|')
            for img_num, info in enumerate(page.get_images(full=True), 1):
                xref = info[0]
                data = doc.extract_image(xref)
                ext = data.get('ext', 'png')
                blob = data['image']
                digest = hashlib.sha1(blob).hexdigest()[:12]
                if digest in seen:
                    continue
                seen.add(digest)
                fname = f'P{pidx}_p{page_num:03d}_img{img_num:02d}_{slug(pdf.stem)}.{ext}'
                target = fig_dir / fname
                target.write_bytes(blob)
                try:
                    w, h, edge = image_stats(target)
                except Exception:
                    target.unlink(missing_ok=True); continue
                if w < args.min_width or h < args.min_height:
                    target.unlink(missing_ok=True); continue
                visual = f'Extracted embedded image; dimensions {w}x{h}px. Inspect manually for semantic content.'
                use = 'Candidate evidence figure; verify against slide assertion before use.'
                rows.append(f'| assets/figures/{fname} | {pdf.name} | {page_num} | {w}x{h} | {edge:.1f} | {context} | {visual} | {use} |')
        doc.close()
    (out / 'figures_index.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    (out / 'source_index.md').write_text('\n'.join(sources) + '\n', encoding='utf-8')
    print(f'Indexed {max(0, len(rows)-2)} figures from {len(papers)} PDFs.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
