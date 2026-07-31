"""Package foundation smoke tests."""

import semantic_runtime


def test_package_importable():
    assert semantic_runtime.__version__ == "0.2.0"


def test_blueprint_packages_exist():
    from semantic_runtime import context, core, evidence, loaders, mcp, models, safety

    assert all(m is not None for m in (context, core, evidence, loaders, mcp, models, safety))

