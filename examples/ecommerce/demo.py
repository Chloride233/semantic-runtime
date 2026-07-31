"""Semantic Runtime demo: resolve a business question with any semantic pack.

Shows the full pipeline: semantic pack loading, context resolution, metric
dependency discovery, relationship resolution, and evidence output.
Optionally serves the model over MCP (--mcp).

Usage:
    python examples/ecommerce/demo.py
    python examples/ecommerce/demo.py --pack saas --question "Why did MRR grow last quarter?"
    python examples/ecommerce/demo.py --pack game --mcp
"""

from __future__ import annotations

import argparse
import sys

from semantic_runtime.core import SemanticRuntime
from semantic_runtime.packs import PACKS, load_pack

PACK_QUESTIONS = {
    "ecommerce": "Why did revenue decrease last month?",
    "saas": "Why did MRR grow last quarter?",
    "finance": "What is the portfolio value?",
    "game": "What is the average revenue per paying user?",
    "healthcare": "What is the readmission rate?",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Semantic Runtime demo")
    parser.add_argument("--mcp", action="store_true", help="serve the model over MCP (stdio) instead of printing")
    parser.add_argument("--pack", default="ecommerce", choices=PACKS, help="semantic pack to demo")
    parser.add_argument("--question", help="question to resolve (defaults to the pack's demo question)")
    args = parser.parse_args(argv)

    runtime = SemanticRuntime(load_pack(args.pack))
    question = args.question or PACK_QUESTIONS[args.pack]

    if args.mcp:
        from semantic_runtime.mcp import create_server

        create_server(runtime).run()
        return 0

    context = runtime.resolve_context(question)

    print("Semantic Runtime demo")
    print(f"Pack: {args.pack}")
    print(f"Question: {question}")
    print()

    if not context.metrics:
        print("No metric matched the question.")
        return 1

    metric = context.metrics[0]
    print(f"1. Identified metric: {metric.id}")
    print(f"   definition: {metric.definition}")
    print(f"   unit: {metric.unit or 'n/a'}, subject entity: {metric.entity}")

    dependencies = runtime.metric_dependencies(metric.id)
    if dependencies:
        print(f"2. Metric dependencies ({[m.id for m in dependencies]})")
        for dependency in dependencies:
            print(f"   {dependency.id}: {dependency.definition}")
    else:
        print("2. Metric dependencies: none")

    related_entities: list = []
    for entity in context.entities:
        related_entities.append(entity)
    if metric.entity and not related_entities:
        related_entities.append(runtime.entity(metric.entity))

    relations_by_id = {r.id: r for r in context.relations}
    for entity in related_entities:
        for relation in runtime.relations_for(entity.id):
            relations_by_id[relation.id] = relation

    affected = {e.id: e for e in related_entities}
    for relation in relations_by_id.values():
        for endpoint in (relation.source, relation.target):
            if endpoint not in affected:
                affected[endpoint] = runtime.entity(endpoint)

    print(f"3. Affected entities ({list(affected)})")
    for entity in affected.values():
        print(f"   {entity.id}: {entity.description}")
    for relation in relations_by_id.values():
        print(f"   relation: {relation.source} -[{relation.type}]-> {relation.target}")

    factors_by_id = {e.id: e for e in context.evidences}
    evidence_terms = set(context.matched_terms)
    evidence_terms.update(e.id for e in affected.values())
    for evidence in runtime.evidences():
        if evidence.id in factors_by_id:
            continue
        if _matches(evidence, evidence_terms):
            factors_by_id[evidence.id] = evidence

    print(f"4. Related factors ({len(factors_by_id)})")
    for evidence in factors_by_id.values():
        print(f"   [{evidence.status}] {evidence.statement}")
        print(f"      source: {evidence.source}")

    print()
    print(f"5. Operation validation: query={runtime.validate('runtime.query').allow}, "
          f"mutate={runtime.validate('runtime.mutate').allow}")
    return 0


def _matches(evidence, terms: set[str]) -> bool:
    from semantic_runtime.context.resolver import ContextResolver

    return bool(ContextResolver._score(evidence.statement, evidence.source, terms=terms))


if __name__ == "__main__":
    sys.exit(main())
