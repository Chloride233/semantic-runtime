"""Integration tests: benchmark and safety evaluation scripts run cleanly."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV = {**os.environ.copy(), "PYTHONPATH": str(REPO_ROOT / "src")}


def run_script(name: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "benchmarks" / name), *args],
        capture_output=True,
        text=True,
        env=ENV,
        cwd=REPO_ROOT,
        timeout=timeout,
    )


def test_runner_runs_all():
    result = run_script("runner.py", "--domain", "ecommerce", timeout=120)
    assert "benchmark" in result.stdout.lower() or "Benchmark" in result.stdout
    assert "by type:" in result.stdout
    assert "SRB score:" in result.stdout
    assert "safety:" in result.stdout


def test_runner_with_type_filter():
    result = run_script("runner.py", "--domain", "ecommerce", "--type", "metric_dependency")
    assert result.returncode == 0, result.stderr
    assert "Metric Dependency" in result.stdout
    assert "1.000" in result.stdout


def test_runner_json_output(tmp_path):
    output = tmp_path / "report.json"
    result = run_script("runner.py", "--domain", "ecommerce", "--output", str(output))
    assert result.returncode != 2, result.stderr
    assert output.exists()
    import json
    doc = json.loads(output.read_text())
    assert "domain" in doc
    assert "srb" in doc
    assert "questions" in doc


def test_benchmark_script_runs():
    result = run_script("run_benchmark.py")
    assert "Phase 6 benchmark: ecommerce" in result.stdout
    assert "by type:" in result.stdout
    assert "overall f1:" in result.stdout


def test_safety_eval_script_runs():
    result = run_script("run_safety_eval.py")
    assert "detection rate:" in result.stdout
    assert "false positive rate:" in result.stdout
    assert "1.000" in result.stdout


def test_runner_safety_only():
    result = run_script("runner.py", "--domain", "ecommerce", "--safety", timeout=120)
    assert result.returncode == 0, result.stderr
    assert "Safety Validation" in result.stdout
    assert "detection=" in result.stdout
