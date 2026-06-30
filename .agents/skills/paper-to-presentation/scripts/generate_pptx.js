#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import pptxgen from 'pptxgenjs';

function arg(name, fallback) {
  const idx = process.argv.indexOf(`--${name}`);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : fallback;
}
function parseSlides(markdown) {
  const chunks = markdown.split(/^## Slide /m).slice(1);
  return chunks.map((chunk) => {
    const lines = chunk.trim().split('\n');
    const title = lines[0].replace(/^\d+:\s*/, '').trim();
    const bullets = [];
    let figure = 'none';
    for (const line of lines) {
      if (line.startsWith('- Figure:')) figure = line.replace('- Figure:', '').trim();
      if (line.trim().startsWith('- ') && line.startsWith('  - ')) bullets.push(line.trim().slice(2));
    }
    return { title, bullets, figure };
  });
}
const configPath = arg('config', 'prd/presentation_config.json');
const specPath = arg('spec', 'prd/slide_specs.md');
const outPath = arg('out', 'output/final_presentation.pptx');
const cfg = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};
const slides = parseSlides(fs.readFileSync(specPath, 'utf8'));
fs.mkdirSync(path.dirname(outPath), { recursive: true });
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = cfg.author || 'Codex';
pptx.subject = 'Sourced paper presentation';
pptx.title = cfg.title || 'Paper-to-Presentation Draft';
pptx.company = 'Generated with Codex paper-to-presentation skill';
pptx.lang = 'en-US';
pptx.theme = { headFontFace: 'Segoe UI', bodyFontFace: 'Segoe UI', lang: 'en-US' };
const theme = cfg.theme || {};
const dark = theme.dark || '21295C';
const primary = theme.primary || '065A82';
const light = theme.light || 'F2F2F2';
const white = theme.white || 'FFFFFF';
const notes = [];
slides.forEach((s, idx) => {
  const slide = pptx.addSlide();
  const isCover = idx === 0;
  slide.background = { color: isCover ? dark : white };
  if (isCover) {
    slide.addText(cfg.title || s.title, { x: 0.8, y: 1.7, w: 11.7, h: 0.7, fontFace: 'Segoe UI', fontSize: 30, bold: true, color: white });
    slide.addText(cfg.subtitle || s.title, { x: 0.85, y: 2.55, w: 11.2, h: 0.35, fontSize: 16, color: light });
    slide.addText(cfg.author || '', { x: 0.85, y: 4.9, w: 8, h: 0.3, fontSize: 12, color: light });
  } else {
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.55, fill: { color: primary }, line: { color: primary } });
    slide.addText(s.title, { x: 0.55, y: 0.1, w: 12.1, h: 0.35, fontSize: 17, bold: true, color: white, fit: 'shrink' });
    slide.addText(s.bullets.slice(0, 4).join('\n'), { x: 0.75, y: 1.05, w: s.figure && s.figure !== 'none' ? 5.8 : 11.6, h: 4.6, fontSize: 15, color: '222222', breakLine: false, bullet: { type: 'ul' }, fit: 'shrink' });
    if (s.figure && s.figure !== 'none' && fs.existsSync(s.figure)) {
      slide.addImage({ path: s.figure, x: 7.0, y: 1.1, w: 5.4, h: 3.7, sizing: { type: 'contain', x: 7.0, y: 1.1, w: 5.4, h: 3.7 } });
    }
    slide.addText(String(idx + 1), { x: 12.35, y: 7.05, w: 0.5, h: 0.2, fontSize: 9, color: '666666' });
  }
  notes.push(`## Slide ${idx + 1}: ${s.title}\n\nProvenance: see prd/source_map.md and source notes in prd/slide_specs.md.\n\nSpeaker notes outline: hook → claim → evidence → transition.\n`);
});
await pptx.writeFile({ fileName: outPath });
const notesPath = cfg.speaker_notes || 'output/speaker_notes.md';
fs.mkdirSync(path.dirname(notesPath), { recursive: true });
fs.writeFileSync(notesPath, notes.join('\n'), 'utf8');
console.log(`Wrote ${outPath} and ${notesPath}`);
