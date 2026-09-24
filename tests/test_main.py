"""Behavior tests for the `python -m llmsquire` CLI."""
from __future__ import annotations

import os

import pytest

from llmsquire import __main__ as cli


class RecordingSensei:
    """Stand-in for Sensei that records the path it was asked to run."""

    calls = []

    def __init__(self, path=None):
        self.path = path
        RecordingSensei.calls.append(self)

    def run(self):
        return True


@pytest.fixture
def sensei(monkeypatch):
    RecordingSensei.calls = []
    monkeypatch.setattr("llmsquire.sensei.Sensei", RecordingSensei)
    return RecordingSensei


def test_no_arguments_runs_the_whole_path(sensei):
    assert cli.main([]) == 0
    assert sensei.calls[-1].path is None


def test_bare_name_runs_only_that_koan(sensei):
    assert cli.main(["about_invocation"]) == 0
    assert sensei.calls[-1].path == ["koans.about_invocation"]


def test_several_koans_run_in_the_order_given(sensei):
    cli.main(["about_statelessness", "about_invocation"])
    assert sensei.calls[-1].path == [
        "koans.about_statelessness", "koans.about_invocation"
    ]


@pytest.mark.parametrize("name", [
    "about_invocation",
    "about_invocation.py",
    "koans.about_invocation",
    "koans/about_invocation",
    "koans/about_invocation.py",
])
def test_name_forms_resolve_to_the_same_module(sensei, name):
    cli.main([name])
    assert sensei.calls[-1].path == ["koans.about_invocation"]


def test_absolute_path_resolves(sensei):
    cli.main([os.path.join(cli._koans_dir, "about_invocation.py")])
    assert sensei.calls[-1].path == ["koans.about_invocation"]


def test_duplicate_names_run_once(sensei):
    cli.main(["about_invocation", "koans.about_invocation"])
    assert sensei.calls[-1].path == ["koans.about_invocation"]


def test_unknown_koan_fails_with_available_names(sensei, capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["about_nonsense"])
    assert exit_info.value.code == 2
    stderr = capsys.readouterr().err
    assert "unknown koan: about_nonsense" in stderr
    assert "about_invocation" in stderr
    assert sensei.calls == []


def test_list_prints_the_curriculum_without_running(sensei, capsys):
    assert cli.main(["--list"]) == 0
    assert capsys.readouterr().out.splitlines() == cli.koan_names()
    assert sensei.calls == []
