"""Unit tests for the YAML model loader."""

import pytest

from semantic_runtime.loaders import load, loads
from semantic_runtime.loaders.yaml_loader import ModelLoadError
from semantic_runtime.models import Entity, Evidence, Metric, Policy, Relation

VALID_DOCUMENT = """
entity:
  id: customer
  type: business_object
relation:
  source: customer
  target: order
  type: places
metric:
  id: revenue
  definition: completed payment minus refunds
evidence:
  id: ev-1
  statement: Revenue dropped 12% in Q2
  source: sql:revenue_report
  status: verified
policy:
  id: p-1
  action: execute.query
  effect: allow
"""


def test_loads_all_five_kinds():
    models = loads(VALID_DOCUMENT)
    assert len(models) == 5
    assert all(isinstance(m, (Entity, Relation, Metric, Evidence, Policy)) for m in models)
    assert models[0] == Entity(id="customer", type="business_object")
    assert models[1].id == "customer:places:order"
    assert models[4] == Policy(id="p-1", action="execute.query", effect="allow")


def test_loads_plural_list_form():
    models = loads(
        """
entities:
  - id: customer
    type: business_object
  - id: order
    type: business_object
"""
    )
    assert len(models) == 2
    assert models[0].id == "customer"
    assert models[1].id == "order"


def test_loads_empty_document():
    assert loads("") == []
    assert loads("# only a comment") == []


def test_loads_unknown_kind():
    with pytest.raises(ModelLoadError, match="unknown model kind"):
        loads("widget:\n  id: w1\n")


def test_loads_non_mapping_top_level():
    with pytest.raises(ModelLoadError, match="mapping"):
        loads("- entity\n- relation\n")


def test_loads_invalid_yaml():
    with pytest.raises(ModelLoadError, match="invalid YAML"):
        loads("entity: [unclosed")


def test_loads_invalid_model_raises_load_error():
    with pytest.raises(ModelLoadError, match="Entity.id"):
        loads("entity:\n  id: ''\n  type: business_object\n")


def test_loads_unknown_field_raises_load_error():
    with pytest.raises(ModelLoadError, match="unexpected field"):
        loads("entity:\n  id: customer\n  type: business_object\n  color: blue\n")


def test_loads_non_mapping_entry():
    with pytest.raises(ModelLoadError, match="mapping per model"):
        loads("entities:\n  - nope\n")


def test_load_from_file(tmp_path):
    path = tmp_path / "model.yaml"
    path.write_text(VALID_DOCUMENT, encoding="utf-8")
    models = load(path)
    assert len(models) == 5


def test_load_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load(tmp_path / "missing.yaml")
