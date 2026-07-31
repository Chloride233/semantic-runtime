---
title: "Semantic Runtime Data Model Specification"
date: 2026-07-31
tags: [semantic-runtime, data-model, entity, relation, v0.1]
status: draft
aliases: [SR Data Model]
---

## Core Models

Entity: Represents business objects.

Relation: Represents connections.

Metric: Represents business meaning.

Evidence: Represents verification sources.

Policy: Represents runtime rules.

## Entity Example

``` yaml
entity:
  id: customer
  type: business_object
```

## Relation Example

``` yaml
relation:
  source: customer
  target: order
```

## Metric Example

``` yaml
metric:
  id: revenue
  definition: completed payment minus refunds
```

> [!info] 协议层对应
> 核心对象在 MCP 层的暴露方式参见 [[Semantic Runtime Protocol Specification]]

## Design Principle

Entity describes what exists.

Relation describes how things connect.

Metric describes meaning.

Evidence describes trust.

Policy describes permissions.
