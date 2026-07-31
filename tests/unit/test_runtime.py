"""Unit tests for the SemanticRuntime facade."""

import pytest

from semantic_runtime.core import EntityNotFoundError, ModelNotLoadedError, PolicyDecision, SemanticRuntime

MODEL_YAML = """
entities:
  - id: customer
    type: business_object
    description: A customer who places orders
  - id: order
    type: business_object
    description: A placed order
relations:
  - source: customer
    target: order
    type: places
metrics:
  - id: revenue
    definition: completed payment minus refunds
    entity: order
policies:
  - id: p-query
    action: execute.query
    effect: allow
  - id: p-delete
    action: delete.order
    effect: deny
"""


def test_load_from_yaml_text():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    assert runtime.entity("customer").description == "A customer who places orders"
    assert runtime.metric("revenue").definition == "completed payment minus refunds"
    assert len(runtime.relations()) == 1
    assert len(runtime.policies()) == 2


def test_load_from_file(tmp_path):
    path = tmp_path / "model.yaml"
    path.write_text(MODEL_YAML, encoding="utf-8")
    runtime = SemanticRuntime.load(path)
    assert {e.id for e in runtime.entities()} == {"customer", "order"}


def test_entity_not_found_code():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    with pytest.raises(EntityNotFoundError) as exc:
        runtime.entity("ghost")
    assert exc.value.code == "ENTITY_NOT_FOUND"


def test_resolve_context_via_runtime():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    context = runtime.resolve_context("Why did revenue drop?")
    assert {m.id for m in context.metrics} == {"revenue"}


def test_validate_allowed_action():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    decision = runtime.validate("execute.query")
    assert isinstance(decision, PolicyDecision)
    assert decision.allow is True
    assert decision.policy_id == "p-query"


def test_validate_denied_action():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    decision = runtime.validate("delete.order")
    assert decision.allow is False
    assert decision.policy_id == "p-delete"


def test_validate_default_deny_without_policy():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    decision = runtime.validate("unknown.action")
    assert decision.allow is False
    assert decision.policy_id is None


def test_validate_deny_wins_over_allow():
    runtime = SemanticRuntime.from_yaml(
        """
policies:
  - id: p-a
    action: execute.query
    effect: allow
  - id: p-b
    action: execute.query
    effect: deny
"""
    )
    assert runtime.validate("execute.query").allow is False


def test_validate_with_safe_sql_allowed():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    decision = runtime.validate("execute.query", sql="SELECT * FROM orders WHERE id = 1")
    assert decision.allow is True


def test_empty_runtime_raises_model_not_loaded():
    runtime = SemanticRuntime()
    with pytest.raises(ModelNotLoadedError):
        runtime.resolve_context("revenue")
    with pytest.raises(ModelNotLoadedError):
        runtime.validate("execute.query")


def test_validate_with_unsafe_sql_denied():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    decision = runtime.validate("execute.query", sql="DELETE FROM orders")
    assert decision.allow is False
    assert decision.policy_id is None
    assert "UNSAFE_DELETE_NO_WHERE" in decision.reason


def test_validate_model_ok_for_valid_model():
    runtime = SemanticRuntime.from_yaml(MODEL_YAML)
    assert runtime.validate_model().ok


def test_validate_model_reports_broken_relations():
    runtime = SemanticRuntime.from_yaml(
        """
entities:
  - id: customer
    type: business_object
relations:
  - source: customer
    target: ghost
    type: places
metrics:
  - id: revenue
    definition: x
    entity: ghost
"""
    )
    report = runtime.validate_model()
    assert not report.ok
    assert {v.code for v in report.violations} == {"RELATION_TARGET_MISSING", "METRIC_ENTITY_MISSING"}


def test_custom_safety_provider_denies_operation():
    from semantic_runtime.safety import SafetyReport, SafetyViolation

    class DenyAllProvider:
        def check_operation(self, action, sql):
            return SafetyReport([SafetyViolation("CUSTOM_DENY", "denied by custom provider")])

    runtime = SemanticRuntime.from_yaml(MODEL_YAML, safety_provider=DenyAllProvider())
    decision = runtime.validate("execute.query")
    assert decision.allow is False
    assert "CUSTOM_DENY" in decision.reason


def test_custom_safety_provider_allows_operation():
    from semantic_runtime.safety import SafetyReport

    class AllowAllProvider:
        def check_operation(self, action, sql):
            return SafetyReport()

    runtime = SemanticRuntime.from_yaml(MODEL_YAML, safety_provider=AllowAllProvider())
    decision = runtime.validate("execute.query", sql="DELETE FROM orders")
    assert decision.allow is True
    assert decision.policy_id == "p-query"


def test_provider_protocol_is_runtime_checkable():
    from semantic_runtime.safety import GuardrailSafetyProvider, SafetyProvider

    assert isinstance(GuardrailSafetyProvider(), SafetyProvider)


def test_metric_dependencies_transitive():
    runtime = SemanticRuntime.from_yaml(
        """
metrics:
  - id: margin
    definition: gross margin ratio
    entity: order
    depends_on: [gross_profit, revenue]
  - id: gross_profit
    definition: revenue minus cost
    entity: order
    depends_on: [revenue]
  - id: revenue
    definition: completed payment minus refunds
    entity: order
"""
    )
    assert [m.id for m in runtime.metric_dependencies("margin")] == [
        "revenue",
        "gross_profit",
    ]
    assert [m.id for m in runtime.metric_dependencies("revenue")] == []


def test_metric_dependencies_handles_cycles():
    runtime = SemanticRuntime.from_yaml(
        """
metrics:
  - id: a
    definition: depends on b
    depends_on: [b]
  - id: b
    definition: depends on a
    depends_on: [a]
"""
    )
    assert {m.id for m in runtime.metric_dependencies("a")} == {"b"}
