#!/usr/bin/env python3
"""Extract candidate claims, numeric results, and page-level provenance from PDFs."""
from __future__ import annotations
import argparse, re
from pathlib import Path
import fitz

KEYWORDS = re.compile(r'\b(result|show|demonstrat|improv|outperform|achiev|conclud|propos|method|accuracy|performance|significant|reduce|increase)\w*\b', re.I)
NUMERIC = re.compile(r'\b\d+(?:\.\d+)?\s?(?:%|x|×|ms|s|GB|MB|mm|cm|mA|AUC|F1|AP|fps)?\b')
SENTENCE = re.compile(r'(?<=[.!?])\s+')

def sentences(text: str):
    for sent in SENTENCE.split(' '.join(text.split())):
        if 50 <= len(sent) <= 320:
            yield sent

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--papers', default='papers'); ap.add_argument('--out', default='assets')
    args = ap.parse_args(); out = Path(args.out); out.mkdir(exist_ok=True)
    claims = ['# Curated candidate claims\n']
    data = ['# Candidate numeric results\n']
    source = ['| ID | Paper | Page | Summary | Suggested use |', '|---|---|---:|---|---|']
    sid = 1
    for pidx, pdf in enumerate(sorted(Path(args.papers).glob('*.pdf')), 1):
        claims.append(f'\n## P{pidx}: {pdf.name}\n')
        data.append(f'\n## P{pidx}: {pdf.name}\n')
        doc = fitz.open(pdf)
        for page_num, page in enumerate(doc, 1):
            text = page.get_text('text')
            picked = []
            for sent in sentences(text):
                if KEYWORDS.search(sent):
                    picked.append(sent)
                if len(picked) >= 4:
                    break
            for sent in picked:
                clean = sent.replace('|', '\\|')
                claims.append(f'- [P{pidx}, {pdf.name}, Page {page_num}] {clean}')
                source.append(f'| S{sid:04d} | {pdf.name} | {page_num} | {clean[:180]} | Claim/evidence candidate |')
                sid += 1
                if NUMERIC.search(sent):
                    data.append(f'- [P{pidx}, {pdf.name}, Page {page_num}] {clean}')
        doc.close()
    (out / 'core_text.md').write_text('\n'.join(claims) + '\n', encoding='utf-8')
    (out / 'data_points.md').write_text('\n'.join(data) + '\n', encoding='utf-8')
    existing = out / 'source_index.md'
    prefix = existing.read_text(encoding='utf-8') + '\n\n' if existing.exists() else ''
    existing.write_text(prefix + '\n'.join(source) + '\n', encoding='utf-8')
    print('Wrote assets/core_text.md, assets/data_points.md, and assets/source_index.md')
    return 0
if __name__ == '__main__': raise SystemExit(main())
