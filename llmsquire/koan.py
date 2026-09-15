"""Koan base class and _fill_ sentinel — the foundation for all exercises."""
from __future__ import annotations

import re
from typing import Any, Optional


class FillMeInError(AssertionError):
    """Raised when _fill_ is found where a real value should be."""
    pass


class _FillMeIn:
    """Sentinel value that fails any comparison with a helpful message.

    The learner replaces _fill_ with the correct value. It is deliberately
    verbose enough to not conflict with Python's _ convention (throwaway
    variable in unpacking, REPL last result), but short enough to be
    visually obvious as a blank to fill in.
    """

    _instance: Optional["_FillMeIn"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __eq__(self, other: Any) -> bool:
        return False

    def __ne__(self, other: Any) -> bool:
        return True

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "_fill_"

    def __str__(self) -> str:
        return "_fill_"

    def __hash__(self) -> int:
        return hash("_fill_")

    def __contains__(self, item: Any) -> bool:
        return False


# Singleton sentinel
_fill_ = _FillMeIn()


class Koan:
    """Base class for all koan exercises.

    Provides:
    - self.llm: per-test LLM client with conversation tracing
    - self._fill_: the fill-in sentinel
    - assertion helpers: assert_match, assert_tool_called, etc.
    """

    def __init__(self, name: str = ""):
        self.name = name
        self.failure: Optional[Exception] = None
        self.llm = None
        self._fill_ = _fill_

    def setup(self):
        """Called before each test. Creates a fresh LLM client."""
        from llmsquire.llm_client import create_llm_client
        self.llm = create_llm_client()

    def teardown(self):
        """Called after each test."""
        pass

    @property
    def passed(self) -> bool:
        return self.failure is None

    # --- Assertions ---

    def assert_match(self, expected: str, actual: str, msg: str = "") -> None:
        """Assert that expected is a substring of actual (case-insensitive)."""
        if isinstance(expected, _FillMeIn):
            raise FillMeInError(
                f"You left _fill_ in your code — replace it with the correct value.\n"
                f"  In assert_match(_fill_, ...)"
            )
        if isinstance(actual, _FillMeIn):
            raise FillMeInError(
                f"You left _fill_ in your code — replace it with the correct value.\n"
                f"  In assert_match(..., _fill_)"
            )
        if expected.lower() not in str(actual).lower():
            raise AssertionError(
                msg or f"Expected '{expected}' in response, but it was not found.\n"
                       f"  Actual response: {str(actual)[:200]}..."
            )

    def assert_equal(self, expected: Any, actual: Any, msg: str = "") -> None:
        """Assert equality, with _fill_ detection."""
        if isinstance(expected, _FillMeIn) or isinstance(actual, _FillMeIn):
            raise FillMeInError(
                "You left _fill_ in your code — replace it with the correct value."
            )
        if expected != actual:
            raise AssertionError(
                msg or f"Expected {expected!r} but got {actual!r}"
            )

    def assert_true(self, condition: Any, msg: str = "") -> None:
        """Assert truthiness, with _fill_ detection."""
        if isinstance(condition, _FillMeIn):
            raise FillMeInError(
                "You left _fill_ in your code — replace it with the correct value."
            )
        if not condition:
            raise AssertionError(msg or f"Expected truthy value but got {condition!r}")

    def assert_tool_called(self, response, tool_name: str, msg: str = "") -> None:
        """Assert that a specific tool was called in the response."""
        if isinstance(tool_name, _FillMeIn):
            raise FillMeInError(
                "You left _fill_ in your code — replace it with the tool name."
            )
        tool_calls = getattr(response, 'tool_calls', []) or []
        called_names = [tc.get("name", tc.get("function", {}).get("name", ""))
                        for tc in tool_calls]
        if tool_name not in called_names:
            raise AssertionError(
                msg or f"Expected tool '{tool_name}' to be called, but it was not. "
                       f"Tools called: {called_names or 'none'}"
            )

    def assert_tool_not_called(self, response, tool_name: str, msg: str = "") -> None:
        """Assert that a specific tool was NOT called in the response."""
        if isinstance(tool_name, _FillMeIn):
            raise FillMeInError(
                "You left _fill_ in your code — replace it with the tool name."
            )
        tool_calls = getattr(response, 'tool_calls', []) or []
        called_names = [tc.get("name", tc.get("function", {}).get("name", ""))
                        for tc in tool_calls]
        if tool_name in called_names:
            raise AssertionError(
                msg or f"Expected tool '{tool_name}' to NOT be called, but it was."
            )

    def assert_json_schema(self, response, schema: dict, msg: str = "") -> None:
        """Assert that response content is valid JSON matching the given schema."""
        import json
        if isinstance(schema, _FillMeIn):
            raise FillMeInError(
                "You left _fill_ in your code — replace it with a JSON schema."
            )
        content = getattr(response, 'content', str(response))
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            raise AssertionError(
                msg or f"Response is not valid JSON: {str(content)[:200]}..."
            )
        for key, expected_type in schema.items():
            if key not in data:
                raise AssertionError(
                    msg or f"JSON missing required key '{key}'"
                )
            if not isinstance(data[key], expected_type):
                raise AssertionError(
                    msg or f"JSON key '{key}' has type {type(data[key]).__name__}, "
                           f"expected {expected_type.__name__}"
                )