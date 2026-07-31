"""Unit tests for semantic model validation."""

from datetime import datetime, timezone

import pytest

from semantic_runtime.models import (
    Entity,
    Evidence,
    Metric,
    ModelValidationError,
    Policy,
    Relation,
)


def test_entity_valid():
    entity = Entity(id="customer", type="business_object", name="Customer", description="A customer")
    assert entity.id == "customer"
    assert entity.type == "business_object"
    assert entity.properties == {}


def test_entity_rejects_empty_id():
    with pytest.raises(ModelValidationError) as exc:
        Entity(id="", type="business_object")
    assert exc.value.field == "id"


def test_entity_rejects_blank_type():
    with pytest.raises(ModelValidationError):
        Entity(id="customer", type="   ")


def test_entity_immutable():
    entity = Entity(id="customer", type="business_object")
    with pytest.raises(AttributeError):
        entity.id = "order"


def test_relation_valid_with_defaults():
    relation = Relation(source="customer", target="order")
    assert relation.id == "customer:related_to:order"
    assert relation.type == "related_to"


def test_relation_valid_with_type():
    relation = Relation(source="customer", target="order", type="places", id="customer-places-order")
    assert relation.id == "customer-places-order"


def test_relation_rejects_blank_source():
    with pytest.raises(ModelValidationError):
        Relation(source=" ", target="order")


def test_relation_rejects_blank_type():
    with pytest.raises(ModelValidationError):
        Relation(source="customer", target="order", type="")


def test_metric_valid():
    metric = Metric(id="revenue", definition="completed payment minus refunds", entity="order")
    assert metric.definition == "completed payment minus refunds"


def test_metric_rejects_blank_definition():
    with pytest.raises(ModelValidationError) as exc:
        Metric(id="revenue", definition="")
    assert exc.value.model == "Metric"
    assert exc.value.field == "definition"


def test_metric_rejects_blank_id():
    with pytest.raises(ModelValidationError):
        Metric(id=" ", definition="revenue")


def test_evidence_valid():
    evidence = Evidence(
        id="ev-1",
        statement="Revenue dropped 12% in Q2",
        source="sql:revenue_report",
        status="verified",
        collected_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
    )
    assert evidence.status == "verified"


def test_evidence_defaults_to_unverified():
    evidence = Evidence(id="ev-1", statement="claim", source="doc:report")
    assert evidence.status == "unverified"


def test_evidence_rejects_invalid_status():
    with pytest.raises(ModelValidationError):
        Evidence(id="ev-1", statement="claim", source="doc:report", status="maybe")


def test_evidence_rejects_blank_source():
    with pytest.raises(ModelValidationError):
        Evidence(id="ev-1", statement="claim", source="")


def test_policy_valid():
    policy = Policy(id="p-1", action="execute.query", effect="allow")
    assert policy.effect == "allow"


def test_policy_defaults_to_deny():
    policy = Policy(id="p-1", action="execute.query")
    assert policy.effect == "deny"


def test_policy_rejects_invalid_effect():
    with pytest.raises(ModelValidationError):
        Policy(id="p-1", action="execute.query", effect="grant")


def test_policy_rejects_blank_action():
    with pytest.raises(ModelValidationError):
        Policy(id="p-1", action="  ")
