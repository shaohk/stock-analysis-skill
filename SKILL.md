---
name: stock-analysis
description: 多Agent股票分析框架 — 支持全流程（15个Agent协作）和指定分析师独立分析两种模式
allowed-tools: Agent, Read, Write, Glob, Bash, WebSearch, WebFetch
credentials:
  - name: TUSHARE_TOKEN
    description: Tushare Token，用于获取A股结构化数据（行情、财务、资金流等）
    how_to_get: "https://tushare.pro/register"
  - name: TUSHARE_URL
    description: Tushare API 地址，如使用自定义节点则填对应地址
requirements:
  python: ">=3.9"
  packages:
    - name: tushare
    - name: pandas
  environment_variables:
    - name: TUSHARE_TOKEN
      required: true
      sensitive: true
    - name: TUSHARE_URL
      required: true
      sensitive: false
---

# Stock Analysis 多Agent股票分析框架

通过 Claude Code 的 Agent tool 编排 15 个专业 Subagent，输出最终投资报告。支持全流程分析和指定分析师独立分析两种模式。

## 快速开始

当用户请求分析股票时，读取详细流程：

```
读取: ~/.claude/skills/stock-analysis/commands/stock-analysis.md
```

## 使用示例

### 全流程分析（默认）
- "分析 600519"（A股茅台）
- "分析 00700.HK"（港股腾讯）
- "全流程分析 000564"

### 指定分析师分析（独立运行）
- "技术分析 600519"
- "只跑基本面和情绪分析师 000564"
- "新闻分析师 00700.HK"
- "全球宏观和产业链分析师分析 600519"

**分析师简称对照：**

| 简称 | 分析师 |
|------|--------|
| 技术 | 技术分析师 |
| 新闻/消息面 | 新闻分析师 |
| 市场/大盘 | 市场分析师 |
| 基本面/财务 | 基本面分析师 |
| 情绪/资金情绪 | 情绪分析师 |
| 中国/国内市场 | 中国市场分析师 |
| 社媒/舆情/社交 | 社交媒体分析师 |
| 全球/宏观 | 全球宏观分析师 |
| 产业链/上下游 | 上下游产业链分析师 |

## 架构说明

**新架构（无进程泄露问题）：**
- 使用 Claude Code 内置的 Agent tool 启动 subagent
- 进程由 Claude Code 内核管理，不会出现孤儿进程
- 每个 subagent 可以使用 WebSearch/WebFetch 等工具

**数据获取：**
- Phase 1 各分析师优先通过 tushare 获取结构化数据（行情、财务、资金流）
- 调用方式：`uv run ~/.claude/skills/stock-analysis/scripts/stock_data_demo.py`
- tushare 数据不足时，使用 WebSearch 补充（实时新闻、舆情、政策解读等）
- 详见各分析师 prompt 中的【数据获取】段落

**分析流程：**
1. Phase 1: 9个分析师并行（技术/新闻/市场/基本面/情绪/中国/社媒/全球宏观/产业链）
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
├── scripts/
│   ├── stock_data_demo.py      # tushare 数据获取脚本
│   └── fund_data_demo.py       # tushare 基金数据脚本
├── references/
│   └── 数据接口.md             # tushare 全量接口参考
└── prompts/
    ├── technical.md            # 技术分析师 prompt
    ├── news.md                 # 新闻分析师 prompt
    ├── market.md               # 市场分析师 prompt
    ├── fundamentals.md         # 基本面分析师 prompt
    ├── sentiment.md            # 情绪分析师 prompt
    ├── china.md                # 中国市场分析师 prompt
    ├── social_media.md         # 社交媒体分析师 prompt
    ├── global_macro.md         # 全球宏观分析师 prompt
    ├── supply_chain.md         # 上下游产业链分析师 prompt
    ├── bull.md                 # 多头研究员 prompt
    ├── bear.md                 # 空头研究员 prompt
    ├── aggressive.md           # 激进分析师 prompt
    ├── neutral.md              # 中性分析师 prompt
    ├── conservative.md         # 保守分析师 prompt
    ├── risk_manager.md         # 风险经理 prompt
    ├── research_manager.md     # 研究经理 prompt
    └── trader.md               # 交易员 prompt
```

## 环境变量配置

使用前必须设置以下环境变量：

```bash
export TUSHARE_TOKEN=你的Token
export TUSHARE_URL=http://118.89.66.41:8010/
```

> tushare-data 已合并至本 skill，参考 `scripts/stock_data_demo.py` 获取数据。

## 报告输出

- 所有报告保存在: `/tmp/stock-analysis/{股票代码}/reports/`
- 最终报告: `/tmp/stock-analysis/{股票代码}/reports/final_trader.md`
