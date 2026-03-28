---
description: 多Agent股票分析框架 — 输入股票代码，经过13个专业Agent协作，输出最终投资报告
allowed-tools: Agent, Read, Write, Glob, Bash, WebSearch, WebFetch
---

# Stock Analysis 多Agent股票分析框架

通过 Claude Code 的 Agent tool 编排 13 个专业 Subagent，输出最终投资报告。

## ⚠️ 数据真实性 + 时效性约束（最高优先级）

**所有 Agent 必须严格遵守以下规则：**

1. **禁止伪造数据：** 所有股价、PE、PB、营收、净利润、毛利率、ROE、目标价等数据，必须来自实际查询结果。严禁凭空捏造或使用假设性数据填充报告。
2. **必须使用最新数据：** 股价必须是最近 3 个交易日内的实际行情；财报必须使用已发布的最新一期（年度或季度）；若最新数据未发布，必须使用最近一期已发布数据并注明报告期。任何"假设当前股价为 XX"的表述一律禁止。
3. **数据过期即无效：** 超过以下时限的数据视为过期，不得直接用于分析：股价超过 5 个交易日、财报超过 2 个季度。过期数据不得作为结论依据，须明确标注数据截止日期并说明对结论的影响。
4. **网络不可用时的处理：** 若 WebSearch/WebFetch/tushare 无法获取实时数据，Agent 必须在报告开头醒目位置标注：`⚠️ 数据说明：本报告因 [网络限制/API不可用/权限不足] 无法获取实时数据，以下 [具体数据类别] 为 [过期数据/推断数据]，请以实际行情为准。` 不得使用过期数据代替实时数据做结论支撑。
5. **数据不可用时不得跳过分析：** 即使无法获取数据，也必须完成分析，但必须在报告开头用独立小节明确说明：哪些数据无法获取、数据截止日期是哪天、基于什么替代信息完成分析。
6. **最终报告必须包含数据来源与可靠性说明：** `final_trader.md` 的报告开头必须包含「数据来源与可靠性说明」小节，逐项标注：① 数据类别 ② 数据来源（实时查询/最近一期已发布/推断） ③ 数据截止日期 ④ 数据可用性评级（A=实时可靠 / B=最近一期 / C=过期/不可得）

---

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
