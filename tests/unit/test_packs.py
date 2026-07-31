"""Unit tests for semantic packs."""

import pytest

from semantic_runtime.core import SemanticRuntime
from semantic_runtime.packs import PackNotFoundError, _load_from, load_pack, pack_path


def test_load_pack_ecommerce():
    models = load_pack("ecommerce")
    runtime = SemanticRuntime(models)
    assert "customer" in {e.id for e in runtime.entities()}
    assert runtime.metric("revenue").definition == "completed payment minus refunds"
    assert runtime.policy("p-allow-read").effect == "allow"


def test_pack_path_is_absolute_file():
    path = pack_path("ecommerce")
    assert path.is_file()
    assert path.name == "semantic_model.yaml"


def test_unknown_pack_raises():
    with pytest.raises(PackNotFoundError, match="unknown semantic pack"):
        load_pack("crypto")
    with pytest.raises(PackNotFoundError, match="unknown semantic pack"):
        pack_path("crypto")


def test_load_pack_from_local_dir(tmp_path):
    source = pack_path("ecommerce")
    target = tmp_path / "models" / "ecommerce" / "semantic_model.yaml"
    target.parent.mkdir(parents=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    models = load_pack("ecommerce", base_dir=tmp_path / "models")
    assert len(models) > 0


def test_load_pack_from_local_file(tmp_path):
    source = pack_path("ecommerce")
    target = tmp_path / "ecommerce.yaml"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    models = _load_from(tmp_path, "ecommerce")
    assert len(models) > 0


def test_load_missing_local_pack_raises(tmp_path):
    with pytest.raises(PackNotFoundError, match="no semantic pack"):
        _load_from(tmp_path, "missing")


@pytest.mark.parametrize("pack", ["ecommerce", "saas", "finance", "game", "healthcare"])
def test_every_pack_loads_and_validates(pack):
    models = load_pack(pack)
    runtime = SemanticRuntime(models)
    assert len(runtime.entities()) >= 4
    assert len(runtime.relations()) >= 3
    assert len(runtime.metrics()) >= 2
    assert len(runtime.policies()) >= 2
    assert runtime.validate_model().ok
    assert runtime.resolve_context("revenue OR mrr OR pnl OR players OR readmission").metrics
