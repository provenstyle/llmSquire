"""The Sensei — runs koans in curriculum order and guards the path."""
from __future__ import annotations

import importlib
import inspect
import os
import traceback
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Iterable, List, Optional, Type

from llmsquire.koan import Koan
from llmsquire.path_to_enlightenment import PATH


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = PROJECT_ROOT / "diagrams"


def render_diagram(trace):
    """Render one test's LLM trace when the diagram generator is available."""
    try:
        from llmsquire.diagram import render
    except ImportError:
        return None
    return render(trace)


class Sensei:
    """Discover and execute koans, halting the journey at the first failure."""

    def __init__(self, path: Optional[Iterable[str]] = None):
        self.path = list(path) if path is not None else PATH

    def discover_koans(self, module: ModuleType) -> List[Type[Koan]]:
        """Return Koan subclasses defined directly in *module*, by class name."""
        return sorted(
            (
                candidate
                for _, candidate in inspect.getmembers(module, inspect.isclass)
                if candidate is not Koan
                and issubclass(candidate, Koan)
                and candidate.__module__ == module.__name__
            ),
            key=lambda koan: koan.__name__,
        )

    def run(self) -> bool:
        """Walk the ordered path; return ``False`` immediately on failure."""
        for module_name in self.path:
            module = importlib.import_module(module_name)
            for koan_class in self.discover_koans(module):
                if not self.run_koan(koan_class):
                    return False
        print("You have reached enlightenment.")
        return True

    def run_koan(self, koan_class: Type[Koan]) -> bool:
        """Run a koan's ``test_`` methods alphabetically, stopping on failure."""
        test_names = sorted(
            name
            for name, member in inspect.getmembers(koan_class, predicate=callable)
            if name.startswith("test_")
        )
        for test_name in test_names:
            if not self.run_test(koan_class, test_name):
                return False
        return True

    def run_test(self, koan_class: Type[Koan], test_name: str) -> bool:
        """Run one test with lifecycle hooks and always render its trace."""
        koan = koan_class(test_name)
        failure: Optional[Exception] = None

        # Inject _fill_ into the koan module's namespace so student code
        # can use it without importing it.
        module = importlib.import_module(koan_class.__module__)
        if not hasattr(module, "_fill_"):
            from llmsquire.koan import _fill_
            module._fill_ = _fill_

        try:
            koan.setup()
            # Wire the per-test LLM client into the module-level proxy
            # so student code's `from llmsquire import llm` works.
            from llmsquire.proxy import llm as llm_proxy
            llm_proxy._client = koan.llm
            getattr(koan, test_name)()
        except Exception as error:
            failure = error
            koan.failure = error
        finally:
            try:
                koan.teardown()
            except Exception as error:
                if failure is None:
                    failure = error
                    koan.failure = error
            self._render_trace(koan, koan_class, test_name)

        if failure is not None:
            self._print_failure(koan_class, test_name, failure)
            return False
        return True

    @staticmethod
    def _render_trace(koan: Koan, koan_class: Type[Koan], test_name: str) -> None:
        llm = getattr(koan, "llm", None)
        trace = getattr(llm, "trace", []) if llm is not None else []
        diagram = render_diagram(trace)
        diagram_path = Sensei._write_diagram(diagram, koan_class, test_name)
        if diagram_path:
            print(f"Sequence diagram: {diagram_path}")

    @staticmethod
    def _write_diagram(diagram, koan_class: Type[Koan], test_name: str):
        """Persist HTML returned by ``diagram.render`` and return its path."""
        if not isinstance(diagram, str) or not diagram.lstrip().lower().startswith("<!doctype html"):
            return diagram
        DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
        koan_name = koan_class.__module__.rsplit(".", 1)[-1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = DIAGRAMS_DIR / f"{koan_name}_{test_name}_{timestamp}.html"
        path.write_text(diagram, encoding="utf-8")
        return path

    @staticmethod
    def _print_failure(koan_class: Type[Koan], test_name: str, error: BaseException) -> None:
        print(f"Thinking {koan_class.__name__}")
        print(f"  {test_name} has damaged your karma.\n")
        print("You have not yet reached enlightenment ...")
        print(str(error) or error.__class__.__name__)
        print("\nPlease meditate on the following code:")
        print(Sensei._failure_location(error, koan_class, test_name))
        print("\nmountains are merely mountains")

    @staticmethod
    def _failure_location(error: BaseException, koan_class: Type[Koan], test_name: str) -> str:
        """Point at the learner's code — the innermost frame inside the koan's own file.

        Assertion helpers and the LLM client raise from the harness, so the deepest
        frame is usually infrastructure. The koan frame is what the learner edits.
        """
        try:
            source = inspect.getsourcefile(koan_class)
        except (TypeError, OSError):
            source = None
        frames = traceback.extract_tb(error.__traceback__)
        if source:
            koan_file = os.path.realpath(source)
            for frame in reversed(frames):
                if os.path.realpath(frame.filename) == koan_file:
                    return Sensei._format_location(frame.filename, frame.lineno)
        if frames:
            frame = frames[-1]
            return Sensei._format_location(frame.filename, frame.lineno)
        _, line = inspect.findsource(getattr(koan_class, test_name))
        return Sensei._format_location(source or "<unknown>", line + 1)

    @staticmethod
    def _format_location(filename: str, lineno: int) -> str:
        """Render a location as the docs show it — project-relative with a ./ prefix."""
        try:
            relative = Path(filename).resolve().relative_to(PROJECT_ROOT.resolve())
        except ValueError:
            return f"{filename}:{lineno}"
        return f"./{relative}:{lineno}"
