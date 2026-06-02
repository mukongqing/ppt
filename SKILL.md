---
name: paper-to-presentation
description: Use when creating course presentation slides from academic papers. Triggers on: "做 pre", "课程汇报", "论文 PPT", "presentation from papers", "把论文做成 PPT", or any request to turn research papers into slides for an academic talk.
---

# Paper-to-Presentation

将 N 篇学术论文转化为课程汇报 PPT 的标准四阶段管道。每阶段是独立 agent 任务，前一阶段产出是后一阶段的输入。必须串行执行。

## 硬约束（所有阶段强制执行）

### 内容铁律
- 所有内容仅来源于指定论文，不捏造、不扩写、不脑补推导
- 关键数据必须标注论文出处（论文X, 第N页/段）
- 出处放入演讲备注（Speaker Notes），PPT 页面只放核心要点
- 面向受众：物理/工程专业本科生，已修相关基础课，避免复杂推导

### 视觉铁律
- 配色：仅用 Ocean Gradient 三色 `#065A82`(深蓝) / `#1C7293`(蓝绿) / `#21295C`(午夜蓝) + `#FFFFFF`(白) + `#F2F2F2`(浅灰)
- 深色背景仅用于封面/尾页/章节间奏
- 禁止动画、转场、渐变、花哨装饰
- 中文：微软雅黑/黑体；英文数字：Arial；数据：Consolas
- 页边距 ≥ 48px 左右，≥ 36px 上下

### 叙事铁律
- 每页标题是断言式完整结论句（非话题标签），例如"EDT 以 5× 帧率提升保持可比图像质量"而非"EDT 方法介绍"
- 每页 3-5 个要点 + 1 个证据（图/表/数据）
- 演讲备注 45-60 秒口播要点，结构：开场句→核心论点→证据解释→过渡句
- 每页文字量 ≤ 70 词（不含标注）

## 目录结构约定

```
project/
  papers/           # 输入的 N 篇 PDF 论文
  assets/figures/   # agent1 产出：提取的图片素材
  assets/           # agent2 产出：文字素材 + 溯源表
  prd/              # agent3 产出：逐页规格表
  final_presentation.pptx  # agent4 最终产出
```

## 阶段管道

### agent1 — 图片提取
- **工具**：`pdf` skill
- **任务**：从 N 篇论文 PDF 提取所有内嵌图片（原理图/数据图/表格），过滤 < 100px 的小图标
- **产出**：
  - `assets/figures/` — 图片文件，命名规则 `P<N>_<描述>.png`
  - `assets/figures_index.md` — 图片清单，格式：`| 图片 | 论文N | 页码 | PPT用途建议 |`
- **约束**：保留 ≥ 150dpi 等效分辨率，不过度压缩，不改变原图内容

### agent2 — 文字素材提取
- **工具**：`pdf` skill
- **任务**：从 N 篇论文提取结论性语句、关键数据、课程衔接点，标注精确出处
- **产出**：
  - `assets/core_text.md` — 按章分类的结论素材库，格式：`- [论文X, 第N页/段] 原文摘要（保留英文术语）`
  - `assets/source_index.md` — 全文溯源对照表，格式：`| 素材ID | 论文 | 页码/段落 | 内容摘要 | 建议用途 |`
  - `assets/data_points.md` — 关键数据速查表（性能数字、对比表格）
- **约束**：逐条可溯源，保留原文英文关键术语，剔除公式推导和繁复实验细节

### agent3 — PRD 逐页规格
- **工具**：`ppt-creator` skill
- **任务**：基于 agent1+agent2 素材，用金字塔原理生成每页详细规格
- **产出**：
  - `prd/slide_outline.md` — 整体结构 + 时间分配（~15-18 页）
  - `prd/slide_specs.md` — 逐页规格表，每页 10 字段：页码/章节/断言式标题/核心观点/要点(3-5条)/配图/文献溯源/演讲备注/建议版式
  - `prd/source_map.md` — 页面-文献溯源对照表
- **约束**：禁止 ppt-creator 自行编造数据，禁止商业路演腔调，控制在 20 分钟以内

### agent4 — PPTX 生成
- **工具**：`pptx` skill → `pptxgenjs`
- **任务**：读取 agent1+2+3 全部产出，逐页生成 PPTX，应用 Ocean Gradient 配色
- **产出**：`final_presentation.pptx` + `speaker_notes.md`
- **页面模板**：封面(#21295C满版) / 目录(白底) / 标准内容(顶部标题条+底栏页码) / 全图页 / 尾页(#21295C满版)
- **约束**：素材使用相对路径，每页添加演讲备注（含文献溯源），字体仅用 Windows 可用字体

## 起步操作

1. 新建项目文件夹，放入论文 PDF 到 `papers/`
2. 用 `paper-search` CLI 收集论文（如需先搜索）
3. 串行执行 agent1 → agent2 → agent3 → agent4
4. 每个 agent 完成后检查其产出再进入下一步
