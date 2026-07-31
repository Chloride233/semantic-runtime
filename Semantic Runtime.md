---
title: "Semantic Runtime"
date: 2026-07-31
tags:
  - semantic-runtime
  - moc
  - index
status: draft
aliases:
  - SR
  - 语义运行时
---

# Semantic Runtime

> [!abstract] 定位
> Semantic Runtime 是 AI Agent 的开源语义基础设施层——在模型智能和工具能力之间提供 **语义理解**。

Models provide intelligence. Tools provide capability. **Semantic Runtime provides understanding.**

## 文档索引

### 战略层
- [[Semantic Runtime PRD]] — 定位、问题、愿景、范围边界
- [[Semantic Runtime Open Source Strategy]] — 开源定位、采纳策略、生态
- [[Semantic Runtime Future Roadmap]] — Phase 1-5 路线图

### 设计层
- [[Semantic Runtime Protocol Specification]] — MCP 工具、核心对象、协议原则
- [[Semantic Runtime Reference Architecture]] — 架构图、核心模块、已有项目集成
- [[Semantic Runtime Data Model Specification]] — Entity、Relation、Metric、Evidence、Policy

### 工程层
- [[Semantic Runtime API & MCP Specification]] — Python SDK、MCP Tools、错误模型
- [[Semantic Runtime Implementation Blueprint]] — 仓库结构、核心类、里程碑
- [[Semantic Runtime Core Implementation Plan]] — 7 步实施计划、测试策略

### 验证层
- [[Semantic Runtime MVP Demo Design]] — 电商场景演示、运行时流程、证据输出
- [[Semantic Runtime Validation and Adoption Plan]] — 真实环境验证框架、采纳策略、成功标准

## 核心概念

| 概念 | 定义 | 文档 |
|------|------|------|
| Entity | 有意义的真实世界对象 | [[Semantic Runtime Data Model Specification\|Data Model]] |
| Relation | 实体之间的连接 | [[Semantic Runtime Protocol Specification\|Protocol]] |
| Metric | 业务级别的度量定义 | [[Semantic Runtime Data Model Specification\|Data Model]] |
| Evidence | 可追溯的验证来源 | [[Semantic Runtime Protocol Specification\|Protocol]] |
| Policy | 运行时规则与权限控制 | [[Semantic Runtime Data Model Specification\|Data Model]] |

## 关联项目

- **Semantic Lighthouse** — 本体治理、语义定义、证据工作流
- **JoinLint** — SQL 安全、关系验证、执行护栏

## 架构总览


