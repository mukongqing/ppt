# Paper-to-Presentation

将学术论文批量转化为课程汇报 PPT 的 Claude Code Skill。四阶段管道：图片提取 → 文字素材 → 叙事设计 → 幻灯片生成。

## 解决的问题

用 AI 做课程 pre 的典型翻车现场：配色花哨、标题空洞（"XX 方法介绍"）、引用格式混乱、演讲时不知道每页该讲多久。这个 Skill 把「从论文到 PPT」拆成四个串行 agent，每阶段产出结构化中间文件，出错时可以精准定位到具体阶段重来，而不是整体推翻。

## 管道概览

```
论文 PDF (papers/)
    │
    ▼
┌──────────────────────────────────────┐
│ agent1  图片提取    pdf skill        │
│         产出: assets/figures/ + 索引  │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ agent2  文字素材    pdf skill        │
│         产出: 结论库 + 溯源表 + 数据表 │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ agent3  叙事设计    ppt-creator skill │
│         产出: 逐页规格表 (15-18页)    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ agent4  幻灯片生成  pptx skill       │
│         产出: final_presentation.pptx │
└──────────────────────────────────────┘
```

## 核心设计决策

**为什么是四个 agent 而不是一个？** 每个阶段有独立的验证标准。图片漏提了重跑 agent1 即可，不用从头来。每个 agent 的 prompt 短而聚焦，产出质量远高于一个超长 prompt。

**为什么引用放备注不放页面？** 幻灯片给观众看，越干净越好。出处追溯是讲者备查用的，丢 Speaker Notes 里不占视觉空间。

**为什么强制 Ocean Gradient 配色？** 不给 agent 配色的自由度。一旦让它"自己选"，结果必定是AI味浓郁的蓝橙渐变。锁定三色反而省心。

## 约束一览

| 维度 | 规则 |
|------|------|
| 内容来源 | 100% 来自论文原文，不捏造不脑补 |
| 配色 | `#065A82` / `#1C7293` / `#21295C` + 白/浅灰 |
| 标题 | 断言式完整结论句，禁止话题标签 |
| 引用 | 演讲备注内标注 [论文X, 第N页/段] |
| 字体 | 微软雅黑/黑体（中）+ Arial（英数）+ Consolas（数据） |
| 动画 | 零。禁止一切动画、转场、渐变 |
| 字数 | 每页正文 ≤ 70 词 |
| 备注 | 每页 45-60 秒中文口播要点 |

## 安装到 Claude Code

```bash
# 克隆到任意位置
git clone https://github.com/<your-username>/paper-to-presentation.git

# 软链接到 Claude Code skills 目录
ln -s "$(pwd)/paper-to-presentation" ~/.claude/skills/paper-to-presentation
```

或者直接复制 `SKILL.md` 到 `~/.claude/skills/paper-to-presentation/`。

## 依赖

| Skill | 用途 |
|-------|------|
| `pdf` | agent1 图片提取 + agent2 文字提取 |
| `ppt-creator` | agent3 金字塔叙事 + 断言式标题框架 |
| `pptx` | agent4 pptxgenjs 幻灯片生成 |

三个都是 Anthropic 官方 skill，Claude Code 内置。

另外可搭配 `paper-search` CLI 做前置的论文检索（arXiv / Semantic Scholar / PubMed）。

## 目录结构

```
your-pre-project/
  papers/                    # 输入的 N 篇 PDF 论文
  assets/
    figures/                 # agent1 产出：提取的图片
    figures_index.md         # agent1 产出：图片清单
    core_text.md             # agent2 产出：结论素材库
    source_index.md          # agent2 产出：溯源对照表
    data_points.md           # agent2 产出：数据速查表
  prd/
    slide_outline.md         # agent3 产出：整体结构
    slide_specs.md           # agent3 产出：逐页规格
    source_map.md            # agent3 产出：溯源表
  final_presentation.pptx    # agent4 最终产出
  speaker_notes.md           # agent4 演讲备注汇总
```

## 适用场景

- 本科生/研究生课程专题汇报（15-20 分钟）
- 组会论文报告
- 学术会议 poster 转 oral presentation
- 综述论文的图文化输出

## 不适用

- 商业路演/产品发布（叙事风格完全不同）
- 非学术内容
- 单篇论文的 5 分钟闪电 talk（管道过重，用更轻量的方式）

## 许可

MIT
