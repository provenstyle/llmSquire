"""LLM client wrapper — OpenAI-compatible, per-test instance with trace recording."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class InteractionRecord:
    """A single LLM API interaction (one round trip)."""
    request: Dict[str, Any]
    response: Dict[str, Any]
    timestamp: float
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    tool_executions: List[Dict[str, Any]] = field(default_factory=list)


class LLMClient:
    """Per-test LLM client with conversation tracing."""

    def __init__(self, api_base: str, model: str, api_key: str):
        self._api_base = api_base
        self._model = model
        self._api_key = api_key
        self._client = None
        self.trace: List[InteractionRecord] = []

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                base_url=self._api_base,
                api_key=self._api_key,
            )
        return self._client

    def ask(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> "LLMResponse":
        """Single LLM API call. Does NOT handle tool-call loops."""
        used_model = model or self._model
        client = self._get_client()

        request_kwargs: Dict[str, Any] = {
            "model": used_model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            request_kwargs["tools"] = tools

        start = time.time()
        response = client.chat.completions.create(**request_kwargs)
        elapsed_ms = (time.time() - start) * 1000

        choice = response.choices[0]
        content = choice.message.content or ""
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                })

        usage = response.usage
        record = InteractionRecord(
            request=request_kwargs,
            response={
                "content": content,
                "tool_calls": tool_calls,
                "finish_reason": choice.finish_reason,
            },
            timestamp=start,
            latency_ms=elapsed_ms,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            model=used_model,
        )
        self.trace.append(record)

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage=record,
        )

    def converse(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict]] = None,
        tool_implementations: Optional[Dict[str, Callable]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_iterations: int = 10,
    ) -> "LLMResponse":
        """Full tool-call loop handler. Iterates until model stops calling tools."""
        tool_impls = tool_implementations or {}
        current_messages = list(messages)

        for _ in range(max_iterations):
            response = self.ask(
                messages=current_messages,
                tools=tools,
                model=model,
                temperature=temperature,
            )

            if not response.tool_calls:
                return response

            # Append the assistant's tool-call message
            assistant_msg: Dict[str, Any] = {"role": "assistant", "content": response.content}
            if response.tool_calls:
                assistant_msg["tool_calls"] = [
                    {"id": tc["id"], "type": "function",
                     "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                    for tc in response.tool_calls
                ]
            current_messages.append(assistant_msg)

            # Execute each tool and append results
            tool_executions = []
            for tc in response.tool_calls:
                import json
                args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                tool_name = tc["name"]
                tool_start = time.time()
                result = tool_impls.get(tool_name, lambda **kw: f"Tool {tool_name} not implemented")(**args)
                tool_elapsed = (time.time() - tool_start) * 1000
                tool_executions.append({
                    "name": tool_name,
                    "arguments": args,
                    "result": str(result),
                    "execution_ms": tool_elapsed,
                })
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result),
                })

            # Record tool executions on the last trace entry
            if self.trace:
                self.trace[-1].tool_executions = tool_executions

        # Max iterations reached — return last response
        return response  # type: ignore[possibly-undefined]


@dataclass
class LLMResponse:
    """Structured response from an LLM call."""
    content: str
    tool_calls: List[Dict[str, Any]]
    finish_reason: str
    usage: InteractionRecord

    @property
    def text(self) -> str:
        return self.content


def create_llm_client() -> LLMClient:
    """Factory: create an LLM client from environment variables."""
    api_base = os.environ.get("LLMSQUIRE_API_BASE", "https://api.fireworks.ai/inference/v1")
    model = os.environ.get("LLMSQUIRE_MODEL", "accounts/fireworks/models/deepseek-v4-flash-0731")
    api_key = os.environ.get("LLMSQUIRE_API_KEY", "")
    return LLMClient(api_base=api_base, model=model, api_key=api_key)