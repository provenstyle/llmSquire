"""Behavior tests for the Sensei koan runner."""
from __future__ import annotations

import importlib.util
import sys
import types

from llmsquire.koan import Koan


def install_koan_module(monkeypatch, name, *koans):
    """Install an in-memory module containing the supplied koan classes."""
    module = types.ModuleType(name)
    for koan in koans:
        koan.__module__ = name
        setattr(module, koan.__name__, koan)
    monkeypatch.setitem(sys.modules, name, module)
    return module


def test_sensei_runs_koans_in_path_and_test_name_order(monkeypatch):
    from llmsquire.sensei import Sensei

    events = []

    class LaterKoan(Koan):
        def test_zebra(self):
            events.append("later.zebra")

    class FirstKoan(Koan):
        def test_beta(self):
            events.append("first.beta")

        def test_alpha(self):
            events.append("first.alpha")

    install_koan_module(monkeypatch, "test_koans.first", FirstKoan)
    install_koan_module(monkeypatch, "test_koans.later", LaterKoan)
    monkeypatch.setattr("llmsquire.sensei.PATH", ["test_koans.first", "test_koans.later"])
    monkeypatch.setattr("llmsquire.sensei.render_diagram", lambda trace: events.append("diagram"))

    assert Sensei().run() is True
    assert events == [
        "first.alpha", "diagram", "first.beta", "diagram", "later.zebra", "diagram"
    ]


def test_sensei_stops_at_first_failure_prints_zen_and_renders(monkeypatch, capsys):
    from llmsquire.sensei import Sensei

    events = []

    class FailingKoan(Koan):
        def test_alpha(self):
            events.append("failed")
            raise AssertionError("The bowl is empty")

        def test_beta(self):
            events.append("should not run")

    class NextKoan(Koan):
        def test_alpha(self):
            events.append("next koan")

    install_koan_module(monkeypatch, "test_koans.failing", FailingKoan)
    install_koan_module(monkeypatch, "test_koans.next", NextKoan)
    monkeypatch.setattr("llmsquire.sensei.PATH", ["test_koans.failing", "test_koans.next"])
    monkeypatch.setattr("llmsquire.sensei.render_diagram", lambda trace: events.append("diagram"))

    assert Sensei().run() is False

    output = capsys.readouterr().out
    assert "Thinking FailingKoan" in output
    assert "test_alpha has damaged your karma." in output
    assert "You have not yet reached enlightenment" in output
    assert "The bowl is empty" in output
    assert "Please meditate on the following code:" in output
    assert "mountains are merely mountains" in output
    assert events == ["failed", "diagram"]


def test_sensei_runs_setup_teardown_and_renders_after_a_failed_test(monkeypatch):
    from llmsquire.sensei import Sensei

    events = []

    class LifecycleKoan(Koan):
        def setup(self):
            self.llm = types.SimpleNamespace(trace=["interaction"])
            events.append("setup")

        def teardown(self):
            events.append("teardown")

        def test_alpha(self):
            events.append("test")
            raise RuntimeError("broken")

    install_koan_module(monkeypatch, "test_koans.lifecycle", LifecycleKoan)
    monkeypatch.setattr("llmsquire.sensei.PATH", ["test_koans.lifecycle"])
    monkeypatch.setattr(
        "llmsquire.sensei.render_diagram", lambda trace: events.append(("diagram", trace))
    )

    assert Sensei().run() is False
    assert events == ["setup", "test", "teardown", ("diagram", ["interaction"])]


def test_sensei_writes_rendered_diagram_next_to_the_koans(monkeypatch, tmp_path):
    from llmsquire.sensei import Sensei

    class DiagramKoan(Koan):
        def test_alpha(self):
            pass

    install_koan_module(monkeypatch, "test_koans.diagram", DiagramKoan)
    monkeypatch.setattr("llmsquire.sensei.PATH", ["test_koans.diagram"])
    monkeypatch.setattr("llmsquire.sensei.DIAGRAMS_DIR", tmp_path)
    html = "<!doctype html><html>trace</html>"
    monkeypatch.setattr("llmsquire.sensei.render_diagram", lambda trace: html)

    assert Sensei().run() is True
    diagrams = list(tmp_path.glob("diagram_test_alpha_*.html"))
    assert len(diagrams) == 1
    assert diagrams[0].read_text() == html


KOAN_WITH_A_BLANK = """\
from llmsquire.koan import Koan, _fill_


class TempKoan(Koan):
    def test_alpha(self):
        self.assert_match(_fill_, "the response")
"""


def test_failure_location_points_at_the_koan_not_the_harness(monkeypatch, tmp_path, capsys):
    from llmsquire.sensei import Sensei

    module_name = "test_koans.about_temp"
    source = tmp_path / "about_temp.py"
    source.write_text(KOAN_WITH_A_BLANK)
    spec = importlib.util.spec_from_file_location(module_name, source)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    monkeypatch.setattr("llmsquire.sensei.PROJECT_ROOT", tmp_path.resolve())
    monkeypatch.setattr("llmsquire.sensei.render_diagram", lambda trace: None)

    assert Sensei(path=[module_name]).run() is False

    output = capsys.readouterr().out
    assert "./about_temp.py:6" in output
    assert "koan.py:" not in output


def test_failure_location_renders_paths_the_way_the_readme_documents():
    from llmsquire.sensei import PROJECT_ROOT, Sensei

    location = Sensei._format_location(
        str(PROJECT_ROOT / "koans" / "about_invocation.py"), 45
    )
    assert location == "./koans/about_invocation.py:45"
