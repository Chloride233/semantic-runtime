# Semantic Runtime Core Implementation Plan v0.1

## Goal

Build the smallest working runtime.

## Development Order

### Step 1: Package Foundation

Create:

semantic_runtime/

core/ models/ loaders/ mcp/ tests/

### Step 2: Data Models

Implement:

-   Entity
-   Relation
-   Metric
-   Evidence
-   Policy

### Step 3: Model Loader

Support:

-   YAML loading
-   validation
-   runtime object creation

### Step 4: Registry

Store and retrieve semantic objects.

### Step 5: Graph Engine

Support:

-   relation lookup
-   traversal
-   dependency discovery

### Step 6: Context Resolver

Initial version:

deterministic semantic lookup.

No LLM dependency.

### Step 7: MCP Server

Expose runtime capabilities.

## Testing Strategy

Unit tests: - model validation - graph traversal - context resolution

Integration: - MCP interaction - example workflows
