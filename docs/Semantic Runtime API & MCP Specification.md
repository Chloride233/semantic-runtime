---
title: "Semantic Runtime API & MCP Specification"
date: 2026-07-31
tags: [semantic-runtime, api, mcp, sdk, v0.1]
status: draft
aliases: [SR API Spec]
---

## Purpose

Define the external contracts between AI Agents and Semantic Runtime.

## Interfaces

Three layers:

AI Agent \| MCP Interface \| Runtime API \| Core Runtime

> [!info] 运行时实现
> 核心 Runtime 类设计参见 [[Semantic Runtime Implementation Blueprint]]

## Python SDK

Example:

``` python
runtime = Runtime.load("model.yaml")
context = runtime.resolve_context("Why did revenue drop?")
```

Core methods:

-   load
-   entity
-   relation
-   metric
-   resolve_context
-   validate

> [!info] 协议定义
> 核心对象语义参见 [[Semantic Runtime Protocol Specification]]

## MCP Tools

### list_entities

Discover semantic objects.

### describe_entity

Retrieve entity meaning and relations.

### get_metric

Retrieve metric definitions.

### resolve_context

Convert business questions into semantic context.

### validate_operation

Check operation safety.

## Error Model

Common errors:

-   MODEL_NOT_LOADED
-   ENTITY_NOT_FOUND
-   RELATION_NOT_FOUND
-   DUPLICATE_MODEL
-   POLICY_DENIED
-   UNSAFE_OPERATION

All runtime errors carry a stable `code` (as above) and a human-readable
message; codes are exposed as-is over MCP tool errors.

## Boundary

Not responsible for:

-   Agent planning
-   LLM execution
-   SQL execution
-   Workflow orchestration
