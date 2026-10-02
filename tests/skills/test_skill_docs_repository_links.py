"""Generated skill resource links remain usable in a maintained fork."""
import importlib.util
from pathlib import Path
import subprocess

import pytest


@pytest.fixture
def generator():
    path = Path(__file__).resolve().parents[2] / "website/scripts/generate-skill-docs.py"
    spec = importlib.util.spec_from_file_location("skill_docs_generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ci_repository_links_to_fork_resources(generator, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "example/hermes-agent")
    meta = {"source_kind": "optional", "rel_path": "finance/portfolio-alert-routing"}
    actual = generator.rewrite_relative_links("[Guide](references/guide.md)", meta)
    assert actual == "[Guide](https://github.com/example/hermes-agent/blob/main/optional-skills/finance/portfolio-alert-routing/references/guide.md)"


@pytest.mark.parametrize("remote", ["git@github.com:example/hermes-agent.git", "https://github.com/example/hermes-agent.git", "https://github.com/example/hermes-agent"])
def test_local_repository_resolves_from_origin(generator, monkeypatch, remote):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setattr(generator.subprocess, "check_output", lambda *a, **k: remote)
    assert generator.source_repository() == "example/hermes-agent"


def test_missing_remote_uses_official_repository(generator, monkeypatch):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    def missing(*a, **k):
        raise subprocess.CalledProcessError(2, a)
    monkeypatch.setattr(generator.subprocess, "check_output", missing)
    assert generator.source_repository() == "NousResearch/hermes-agent"
