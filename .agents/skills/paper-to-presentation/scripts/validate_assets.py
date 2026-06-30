#!/usr/bin/env python3
"""Validate extracted figure dimensions and flag readability risks."""
from __future__ import annotations
import argparse, math
from pathlib import Path
from PIL import Image, ImageFilter, ImageStat

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--figures', default='assets/figures'); ap.add_argument('--display-width', type=float, default=4.5); ap.add_argument('--display-height', type=float, default=2.5)
    args = ap.parse_args(); rows = ['| Figure | Pixels | Effective DPI | Edge density | Status |', '|---|---:|---:|---:|---|']
    for path in sorted(Path(args.figures).glob('*')):
        try:
            img = Image.open(path).convert('L')
        except Exception:
            continue
        iw, ih = img.size
        dpi = math.sqrt(iw * ih) / math.sqrt(args.display_width * args.display_height)
        edge = ImageStat.Stat(img.filter(ImageFilter.FIND_EDGES)).mean[0]
        unreadable = dpi > 300 and args.display_height < 1.5 and edge > 12
        rows.append(f'| {path.as_posix()} | {iw}x{ih} | {dpi:.1f} | {edge:.1f} | {"UNREADABLE_RISK" if unreadable else "ok"} |')
    report = Path('assets/figure_validation.md'); report.parent.mkdir(exist_ok=True); report.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'Wrote {report}')
    return 0
if __name__ == '__main__': raise SystemExit(main())
