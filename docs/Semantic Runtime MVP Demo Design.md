---
title: "Semantic Runtime MVP Demo Design"
date: 2026-07-31
tags: [semantic-runtime, demo, mvp, v0.1]
status: draft
aliases: [SR Demo]
---

## Goal

Show why AI Agents need semantic runtime.

> [!question] 核心演示问题
> "Why did revenue decrease last month?" — Revenue 指标定义参见 [[Semantic Runtime Data Model Specification]]

## Demo Scenario

Domain: E-commerce

Entities:

-   Customer
-   Order
-   Product
-   Payment

## User Question

Why did revenue decrease last month?

## Runtime Process

1.  Identify Revenue metric.
2.  Find related entities.
3.  Resolve relationships.
4.  Provide evidence context.

## Expected Output

Revenue decreased 12%.

Related factors:

-   customer activity decline
-   payment failures

Evidence:

-   metric definition
-   related data sources

## Demo Requirements

Must show:

-   semantic model loading
-   MCP connection
-   context resolution
-   evidence output
