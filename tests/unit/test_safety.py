"""Unit tests for safety: model validation and SQL guardrails."""

from semantic_runtime.models import Entity, Metric, Relation
from semantic_runtime.safety import check_sql, validate_model
from semantic_runtime.safety.report import SafetyReport

CUSTOMER = Entity(id="customer", type="business_object")
ORDER = Entity(id="order", type="business_object")


def test_valid_model_passes():
    report = validate_model(
        [
            CUSTOMER,
            ORDER,
            Relation(source="customer", target="order", type="places"),
            Metric(id="revenue", definition="payments minus refunds", entity="order"),
        ]
    )
    assert isinstance(report, SafetyReport)
    assert report.ok


def test_relation_with_missing_target_fails():
    report = validate_model([CUSTOMER, Relation(source="customer", target="ghost", type="places")])
    assert not report.ok
    codes = {v.code for v in report.violations}
    assert "RELATION_TARGET_MISSING" in codes


def test_relation_with_missing_source_fails():
    report = validate_model([CUSTOMER, Relation(source="ghost", target="customer", type="places")])
    assert not report.ok
    assert {v.code for v in report.violations} == {"RELATION_SOURCE_MISSING"}


def test_metric_with_missing_entity_fails():
    report = validate_model([Metric(id="revenue", definition="x", entity="ghost")])
    assert {v.code for v in report.violations} == {"METRIC_ENTITY_MISSING"}


def test_metric_with_missing_dependency_fails():
    report = validate_model([Metric(id="margin", definition="x", depends_on=("ghost",))])
    assert {v.code for v in report.violations} == {"METRIC_DEPENDENCY_MISSING"}


def test_sql_select_is_safe():
    report = check_sql("SELECT * FROM orders")
    assert report.ok


def test_sql_update_with_where_is_safe():
    assert check_sql("UPDATE orders SET status = 'paid' WHERE id = 42").ok
    assert check_sql("DELETE FROM orders WHERE status = 'refunded'").ok


def test_sql_update_without_where_is_unsafe():
    report = check_sql("UPDATE orders SET status = 'paid'")
    assert not report.ok
    assert {v.code for v in report.violations} == {"UNSAFE_UPDATE_NO_WHERE"}


def test_sql_delete_without_where_is_unsafe():
    report = check_sql("DELETE FROM orders")
    assert {v.code for v in report.violations} == {"UNSAFE_DELETE_NO_WHERE"}


def test_sql_multiple_statements_is_unsafe():
    report = check_sql("SELECT * FROM orders; DROP TABLE orders")
    assert {v.code for v in report.violations} == {"UNSAFE_MULTI_STATEMENT"}


def test_sql_comments_do_not_confuse_checks():
    assert check_sql("SELECT /* comment */ * FROM orders").ok
    assert check_sql("UPDATE orders SET x = 1 WHERE id = 1 /* trailing */").ok
    assert check_sql("-- comment\nSELECT * FROM orders").ok
    assert not check_sql("UPDATE orders SET x = 1 /* no where needed */").ok


def test_sql_trailing_semicolon_is_safe():
    assert check_sql("SELECT * FROM orders;").ok


def test_sql_whitespace_only_is_safe():
    assert check_sql("   ").ok
