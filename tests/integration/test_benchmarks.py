"""Integration tests: benchmark and safety evaluation scripts run cleanly."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV = {**os.environ.copy(), "PYTHONPATH": str(REPO_ROOT / "src")}


def run_script(name: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "benchmarks" / name)],
        capture_output=True,
        text=True,
        env=ENV,
        cwd=REPO_ROOT,
        timeout=60,
    )


def test_benchmark_script_runs():
    result = run_script("run_benchmark.py")
    assert result.returncode == 0, result.stderr
    assert "Level 2 benchmark: ecommerce" in result.stdout
    assert "averages:" in result.stdout
    assert "entities:" in result.stdout


def test_safety_eval_script_runs():
    result = run_script("run_safety_eval.py")
    assert result.returncode == 0, result.stderr
    assert "detection rate:" in result.stdout
    assert "false positive rate:" in result.stdout
    assert "1.000" in result.stdout
