# Semantic Runtime Data Model Specification v0.1

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

## Design Principle

Entity describes what exists.

Relation describes how things connect.

Metric describes meaning.

Evidence describes trust.

Policy describes permissions.
