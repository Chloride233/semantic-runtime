---
title: "Semantic Runtime Protocol Specification"
date: 2026-07-31
tags: [semantic-runtime, protocol, mcp, v0.1]
status: draft
aliases: [SR Protocol]
---

## Purpose

Define the stable interface between AI Agents and Semantic Runtime.

## Core Objects

### Entity

Meaningful real-world object.

### Relation

Connection between entities.

### Metric

Business-level definition.

### Evidence

Traceable source supporting conclusions.

### Policy

Rules controlling access and execution.

> [!info] 完整 API 规范
> SDK、错误模型和接口边界参见 [[Semantic Runtime API & MCP Specification]]

## MCP Tools

### list_entities

Discover semantic objects.

### describe_entity

Retrieve entity meaning and relationships.

### resolve_context

Resolve business questions into semantic context.

### validate_operation

Check operation safety.

> [!info] 数据模型
> 核心对象的完整定义参见 [[Semantic Runtime Data Model Specification]]

## Protocol Principles

-   Stable primitives
-   Backward compatibility
-   Implementation independence
-   Explicit semantics
