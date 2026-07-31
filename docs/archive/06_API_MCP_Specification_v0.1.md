# Semantic Runtime API & MCP Specification v0.1

## Purpose

Define the external contracts between AI Agents and Semantic Runtime.

## Interfaces

Three layers:

AI Agent \| MCP Interface \| Runtime API \| Core Runtime

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
-   POLICY_DENIED
-   UNSAFE_OPERATION

## Boundary

Not responsible for:

-   Agent planning
-   LLM execution
-   SQL execution
-   Workflow orchestration
