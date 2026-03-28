---
description: 多Agent股票分析框架 — 输入股票代码，经过13个专业Agent协作，输出最终投资报告
allowed-tools: Agent, Read, Write, Glob, Bash, WebSearch, WebFetch
---

# Stock Analysis 多Agent股票分析框架

通过 Claude Code 的 Agent tool 编排 13 个专业 Subagent，输出最终投资报告。

## 使用方法

用户输入股票代码后，按照以下流程执行：

## 执行流程

### 初始化

1. 确认股票代码 `{{TICKER}}`
2. 创建报告目录：`mkdir -p /tmp/stock-analysis/{{TICKER}}/reports`

---

### Phase 1: 分析师层（7个 Agent 并行）

使用 Agent tool 并行启动 7 个分析师 Agent。

**每个 Agent 的 prompt 从对应文件读取：**
- 技术分析师: `~/.claude/skills/stock-analysis/prompts/technical.md`
- 新闻分析师: `~/.claude/skills/stock-analysis/prompts/news.md`
- 市场分析师: `~/.claude/skills/stock-analysis/prompts/market.md`
- 基本面分析师: `~/.claude/skills/stock-analysis/prompts/fundamentals.md`
- 情绪分析师: `~/.claude/skills/stock-analysis/prompts/sentiment.md`
- 中国市场分析师: `~/.claude/skills/stock-analysis/prompts/china.md`
- 社交媒体分析师: `~/.claude/skills/stock-analysis/prompts/social_media.md`

**执行方式：**
```
在一次消息中调用 7 个 Agent tool，实现并行执行
每个 Agent 的 prompt 中将 {{TICKER}} 替换为实际股票代码
```

**等待所有 Phase 1 Agent 完成后，进入 Phase 2。**

---

### Phase 2: 研究员辩论层（2个 Agent 并行）

**前提条件：** Phase 1 全部完成

**构建上下文：** 读取 Phase 1 的 7 份报告，合并作为 context

**Agent 列表：**
- 多头研究员: `~/.claude/skills/stock-analysis/prompts/bull.md`
- 空头研究员: `~/.claude/skills/stock-analysis/prompts/bear.md`

**执行方式：**
- 读取 7 份分析师报告内容
- 将报告内容插入 prompt 的 `{{CONTEXT}}` 占位符
- 并行启动 2 个 Agent

**等待 Phase 2 完成，进入 Phase 3。**

---

### Phase 3: 风险辩论层（3个 Agent 并行）

**前提条件：** Phase 2 全部完成

**构建上下文：** 读取 Phase 1 + Phase 2 的所有报告

**Agent 列表：**
- 激进分析师: `~/.claude/skills/stock-analysis/prompts/aggressive.md`
- 中性分析师: `~/.claude/skills/stock-analysis/prompts/neutral.md`
- 保守分析师: `~/.claude/skills/stock-analysis/prompts/conservative.md`

**执行方式：** 并行启动 3 个 Agent

**等待 Phase 3 完成，进入 Phase 4。**

---

### Phase 4: 风险经理（串行）

**前提条件：** Phase 3 完成

**构建上下文：** 读取所有已有报告

**Agent：** 风险经理: `~/.claude/skills/stock-analysis/prompts/risk_manager.md`

**等待完成后进入 Phase 5。**

---

### Phase 5: 研究经理（串行）

**前提条件：** Phase 4 完成

**构建上下文：** 读取所有已有报告

**Agent：** 研究经理: `~/.claude/skills/stock-analysis/prompts/research_manager.md`

**等待完成后进入 Phase 6。**

---

### Phase 6: 交易员（串行）

**前提条件：** Phase 5 完成

**构建上下文：** 读取所有已有报告

**Agent：** 交易员: `~/.claude/skills/stock-analysis/prompts/trader.md`

**完成后输出最终报告。**

---

## 输出

- 所有报告保存在: `/tmp/stock-analysis/{{TICKER}}/reports/`
- 最终报告: `/tmp/stock-analysis/{{TICKER}}/reports/final_trader.md`

## 支持的股票类型

- **A股**: 6位数字代码（如 `600519`、`000858`、`300750`）
- **港股**: 代码+.HK后缀（如 `00700.HK`、`09988.HK`）

## 关键原则

1. **并行优先**：同一 Phase 内的 Agent 尽可能并行启动
2. **上下文传递**：后续 Phase 必须读取前面所有报告作为 context
3. **文件持久化**：每个 Agent 完成后将报告写入对应文件
4. **进程安全**：使用 Agent tool 而非 subprocess，由 Claude Code 内核管理进程

## 示例执行

当用户说"分析 600519"时：

1. 创建目录 `/tmp/stock-analysis/600519/reports`
2. 并行启动 7 个分析师 Agent
3. 等待完成，读取报告，并行启动多头/空头研究员
4. 等待完成，读取报告，并行启动激进/中性/保守分析师
5. 串行执行风险经理 → 研究经理 → 交易员
6. 输出最终报告路径
