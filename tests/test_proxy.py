"""Tests for the llm proxy that student koan files import."""
import pytest
from llmsquire.proxy import llm, _LLMProxy


class TestLLMProxy:

    def test_proxy_raises_before_client_set(self):
        proxy = _LLMProxy()
        with pytest.raises(RuntimeError, match="not available outside"):
            proxy.ask(messages=[{"role": "user", "content": "hi"}])

    def test_proxy_delegates_ask(self):
        class FakeClient:
            def __init__(self):
                self.trace = []
                self.asked = False

            def ask(self, messages, tools=None, model=None, temperature=0.0):
                self.asked = True
                self.asked_messages = messages
                return "fake_response"

        proxy = _LLMProxy()
        proxy._client = FakeClient()
        result = proxy.ask(messages=[{"role": "user", "content": "hi"}])
        assert result == "fake_response"
        assert proxy._client.asked is True

    def test_proxy_delegates_converse(self):
        class FakeClient:
            def __init__(self):
                self.trace = []

            def converse(self, messages, tools=None, tool_implementations=None,
                         model=None, temperature=0.0, max_iterations=10):
                return "fake_converse"

        proxy = _LLMProxy()
        proxy._client = FakeClient()
        result = proxy.converse(messages=[{"role": "user", "content": "hi"}])
        assert result == "fake_converse"

    def test_proxy_exposes_trace(self):
        class FakeClient:
            def __init__(self):
                self.trace = ["entry1", "entry2"]

        proxy = _LLMProxy()
        proxy._client = FakeClient()
        assert proxy.trace == ["entry1", "entry2"]