---
name: stock-analysis
description: 多Agent股票分析框架 — 输入股票代码，经过13个专业Agent协作，输出最终投资报告
allowed-tools: Agent, Read, Write, Glob, Bash, WebSearch, WebFetch
---

# Stock Analysis 多Agent股票分析框架

通过 Claude Code 的 Agent tool 编排 13 个专业 Subagent，输出最终投资报告。

## 快速开始

当用户请求分析股票时，读取详细流程：

```
读取: ~/.claude/skills/stock-analysis/commands/stock-analysis.md
```

## 使用示例

- "分析 600519"（A股茅台）
- "分析 00700.HK"（港股腾讯）

## 架构说明

**新架构（无进程泄露问题）：**
- 使用 Claude Code 内置的 Agent tool 启动 subagent
- 进程由 Claude Code 内核管理，不会出现孤儿进程
- 每个 subagent 可以使用 WebSearch/WebFetch 等工具

**分析流程：**
1. Phase 1: 7个分析师并行（技术/新闻/市场/基本面/情绪/中国/社媒）
2. Phase 2: 多头/空头研究员辩论
3. Phase 3: 激进/中性/保守风险分析师辩论
4. Phase 4: 风险经理综合评估
5. Phase 5: 研究经理汇总
6. Phase 6: 交易员给出最终决策

## 文件结构

```
~/.claude/skills/stock-analysis/
├── SKILL.md                    # 入口文件（本文件）
├── commands/
│   └── stock-analysis.md       # 详细执行流程
└── prompts/
    ├── technical.md            # 技术分析师 prompt
    ├── news.md                 # 新闻分析师 prompt
    ├── market.md               # 市场分析师 prompt
    ├── fundamentals.md         # 基本面分析师 prompt
    ├── sentiment.md            # 情绪分析师 prompt
    ├── china.md                # 中国市场分析师 prompt
    ├── social_media.md         # 社交媒体分析师 prompt
    ├── bull.md                 # 多头研究员 prompt
    ├── bear.md                 # 空头研究员 prompt
    ├── aggressive.md           # 激进分析师 prompt
    ├── neutral.md              # 中性分析师 prompt
    ├── conservative.md         # 保守分析师 prompt
    ├── risk_manager.md         # 风险经理 prompt
    ├── research_manager.md     # 研究经理 prompt
    └── trader.md               # 交易员 prompt
```

## 报告输出

- 所有报告保存在: `/tmp/stock-analysis/{股票代码}/reports/`
- 最终报告: `/tmp/stock-analysis/{股票代码}/reports/final_trader.md`
