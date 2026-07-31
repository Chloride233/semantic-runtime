---
title: "Semantic Runtime Reference Architecture"
date: 2026-07-31
tags: [semantic-runtime, architecture, v0.1]
status: draft
aliases: [SR Architecture]
---

## Architecture

AI Agent

↓

MCP / SDK / API

↓

Semantic Runtime

↓

Enterprise Systems

> [!info] 实施细节
> 仓库结构和里程碑参见 [[Semantic Runtime Implementation Blueprint]]

## Core Modules

-   Semantic Model Registry
-   Entity Graph
-   Context Resolver
-   Evidence System
-   Policy Engine
-   MCP Gateway

> [!example] 关联项目
> - [[Semantic Runtime PRD|Semantic Lighthouse]] — 本体治理与证据工作流
> - [[Semantic Runtime Future Roadmap|JoinLint]] — SQL 安全与执行护栏 (Phase 4)

## Existing Project Integration

Semantic Lighthouse: - ontology governance - semantic definitions -
evidence workflow

JoinLint: - SQL safety - relationship validation - execution guardrails

## Goal

Build the semantic operating layer for AI Agents.
