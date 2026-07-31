---
title: "Semantic Runtime Benchmark Plan v0.2"
date: 2026-07-31
tags: [semantic-runtime, benchmark, evaluation, v0.2]
status: draft
aliases: [SR Benchmark Plan v0.2]
---

# Semantic Runtime Benchmark Plan v0.2

## 与 v0.1 的核心区别

| 维度 | v0.1 | v0.2 |
|---|---|---|
| 评测架构 | Agent 行为测试 | 拆为 Mode A（Runtime 准确性）+ Mode B（Agent 增强，延后） |
| Agent 适配器 | 每种框架单独写适配器 | MCP server 即通用适配层 |
| MVP 规模 | 3 Agent × 3 领域 × 100 题 | 2 领域 + Mode A 全题型 + 基础框架 |
| 安全评分 | 加法权重 10% | 乘法因子，安全不通过则总分归零 |
| 题型 | 5 种 | 6 种（增加指标依赖分析） |
| 数据集格式 | 完全重新设计 | 基于现有格式扩展，向下兼容 |

---

## 1. 目的

Semantic Runtime 不应该被当作单个 Agent 应用来评估。

要证明的是：

> Semantic Runtime 作为语义基础设施层，自身具备准确的业务理解、安全校验和证据溯源能力。

评测分两个层级，不在同一个 MVP 中交付：

- **Mode A（MVP）**：Runtime 自身能力的确定性/半确定性评测
- **Mode B（v0.3+）**：Agent 接入 Runtime 后的行为改善评测

---

## 2. 评估哲学

不测：

- Agent 能不能调用 Semantic Runtime（一个 Agent 能调用不代表能力）
- 单个 Demo 是否成功

测：

- Runtime 对不同领域问题的语义理解是否准确
- Runtime 的安全校验是否可靠
- 评测框架是否能跨领域复用
- 数据集和评分体系是否稳定

---

## 3. 评测架构

```
                    Benchmark Runner
                          │
          ┌───────────────┼───────────────┐
          │               │               │
     Dataset Loader   Runtime Engine   Evaluator
          │               │               │
          │         ┌─────┴─────┐         │
          │         │           │         │
          │    resolve_context  validate  │
          │         │           │         │
          │         └─────┬─────┘         │
          │               │               │
          └───────────────┼───────────────┘
                          │
                  Benchmark Report
```

---

## 4. 评测模式

### Mode A：Runtime 准确性评测（MVP）

直接调用 `runtime.resolve_context()`、`runtime.validate()`、`runtime.metric_dependencies()` 等 API，与 ground truth 对比。

条件：不需要 Agent，不需要 LLM API key，完全可自动化。

### Mode B：Agent 增强评测（v0.3+）

将 Runtime 作为 MCP server 挂载到 Agent 上，对比裸 Agent vs Agent + Runtime 的回答质量。

条件：需要 LLM Judge、Agent 运行环境、API key。延后实现。

---

## 5. 题型设计（6 种）

| 编号 | 题型 | 评测目标 | Runtime API |
|---|---|---|---|
| T1 | Semantic Understanding | 指标/实体定义理解 | `resolve_context` |
| T2 | Entity Discovery | 业务实体识别 | `resolve_context` |
| T3 | Relationship Reasoning | 实体关系图谱推理 | `resolve_context` + graph API |
| T4 | Metric Dependency | 指标传递性依赖解析 | `metric_dependencies` |
| T5 | Evidence Grounding | 证据溯源匹配 | `resolve_context` |
| T6 | Safety Validation | 操作安全校验 | `validate` + `validate_model` |

### T4 - Metric Dependency（新增）

这是 Semantic Runtime 与普通 schema 工具的核心区别——Runtime 理解指标之间的计算依赖。

示例: `"What metrics does average_order_value depend on?"`

评测传递性依赖链完整性和依赖顺序正确性。

---

## 6. 数据集格式

基于现有 `benchmarks/ecommerce/` 的 JSON 结构扩展，向下兼容。

### 领域目录结构

```
benchmarks/
├── ecommerce/
│   ├── model.yaml
│   ├── questions.json
│   ├── expected_context.json
│   ├── expected_metrics.json       # T4 新增
│   ├── safety_scenarios.json       # T6 新增
│   └── evaluation.json
├── saas/                           # MVP 新增
│   ├── model.yaml
│   ├── questions.json
│   ├── expected_context.json
│   ├── expected_metrics.json
│   ├── safety_scenarios.json
│   └── evaluation.json
├── runner.py
├── scorer.py
└── report.py
```

### questions.json（扩展版）

```json
{
  "domain": "ecommerce",
  "questions": [
    {
      "id": "q-metric-dep-1",
      "type": "metric_dependency",
      "text": "What does average_order_value depend on?"
    },
    {
      "id": "q-safety-1",
      "type": "safety_validation",
      "text": "Calculate revenue by customer segment",
      "validate": {
        "action": "runtime.query",
        "sql": "SELECT customer_id, SUM(amount) FROM orders"
      }
    }
  ]
}
```

### evaluation.json（扩展版）

```json
{
  "name": "ecommerce",
  "categories": ["entities", "relations", "metrics", "evidences"],
  "thresholds": {
    "semantic_understanding": 0.5,
    "entity_discovery": 0.5,
    "relationship_reasoning": 0.5,
    "metric_dependency": 0.7,
    "evidence_grounding": 0.5,
    "safety_validation": 1.0
  }
}
```

---

## 7. 评分体系

### SRB Score

```
SRB = (
    0.25 × semantic_understanding
  + 0.20 × entity_discovery
  + 0.20 × relationship_reasoning
  + 0.15 × metric_dependency
  + 0.10 × evidence_grounding
) × safety_factor

safety_factor = 1.0 if safety_validation >= 1.0 else 0.0
```

### 与 v0.1 评分对比

| 维度 | v0.1 | v0.2 | 理由 |
|---|---|---|---|
| Semantic Understanding | 25% | 25% | 不变 |
| Context Quality / Entity Discovery | 20% | 20% | 不变 |
| Relationship Reasoning | — | 20% | 从 Context Quality 拆出 |
| Metric Dependency | — | 15% | 新增，核心差异化能力 |
| Evidence | 20% | 10% | 降权 |
| Task Completion | 25% | — | 移除，属于 Mode B 范畴 |
| Safety | 10% 加法 | 乘法因子 | 改为硬约束 |

---

## 8. 安全评测

场景从硬编码 Python 列表迁移到 `safety_scenarios.json` 配置文件。

指标：detection rate、false positive rate、accuracy。

---

## 9. 评测 CLI

```bash
# 运行单个领域所有题目
python -m benchmarks.runner --domain ecommerce

# 运行指定题型
python -m benchmarks.runner --domain ecommerce --type metric_dependency

# 仅安全评测
python -m benchmarks.runner --domain ecommerce --safety

# 输出 JSON 报告
python -m benchmarks.runner --domain ecommerce --output report.json
```

---

## 10. MVP 实施范围

### 交付物

1. 统一 Runner (`benchmarks/runner.py`)
2. 评分模块 (`benchmarks/scorer.py`)
3. 报告模块 (`benchmarks/report.py`)
4. Ecommerce 领域扩展 (T4 + T6)
5. 安全场景 JSON 化

### 不做

- Mode B（Agent A/B 评测）
- 其他领域（finance、game、manufacturing）
- LLM Judge
- 人工评审层

---

## 11. 成本评估

| 项目 | 时间估计 | 外部依赖 |
|---|---|---|
| scorer.py + report.py | 0.5 天 | 无 |
| runner.py | 1 天 | 无 |
| ecommerce 题型扩展 | 0.5 天 | 无 |
| safety 场景 JSON 化 | 0.5 天 | 无 |
| 测试更新 | 0.5 天 | 无 |
| **合计** | **3 天** | 0 个外部 API 依赖 |
