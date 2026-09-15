"""Self-contained HTML sequence diagrams for recorded LLM interactions."""
from __future__ import annotations

from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
from typing import Any, Iterable, Sequence

from llmsquire.llm_client import InteractionRecord


def _json(value: Any) -> str:
    """Serialize an API payload faithfully while tolerating unusual values."""
    return json.dumps(value, indent=2, ensure_ascii=False, default=str, sort_keys=True)


def _payload(title: str, value: Any) -> str:
    return (
        '<section class="payload">'
        f"<h4>{escape(title)}</h4>"
        f'<pre class="json">{escape(_json(value))}</pre>'
        "</section>"
    )


def _event(kind: str, label: str, detail: str, payload: str = "") -> str:
    return (
        f'<article class="event {escape(kind)}">'
        '<div class="arrow" aria-hidden="true"></div>'
        '<div class="event-card">'
        f'<h3>{escape(label)}</h3><p class="annotation">{escape(detail)}</p>{payload}'
        "</div></article>"
    )


def _tool_events(executions: Iterable[dict[str, Any]]) -> str:
    events = []
    for execution in executions:
        name = str(execution.get("name", "unknown tool"))
        arguments = execution.get("arguments", {})
        result = execution.get("result", "")
        duration = float(execution.get("execution_ms", 0) or 0)
        events.append(
            _event(
                "tool-call",
                f"Tool call · {name}",
                f"LLM → Tools · {duration:.1f} ms execution",
                _payload("Arguments", arguments),
            )
        )
        events.append(
            _event(
                "tool-result",
                f"Tool result · {name}",
                f"Tools → LLM · {duration:.1f} ms execution",
                _payload("Return value", result),
            )
        )
    return "".join(events)


def render(trace: Sequence[InteractionRecord]) -> str:
    """Return a complete, offline HTML sequence diagram for *trace*.

    Payloads are HTML-escaped before insertion so a model response or tool result
    cannot alter the diagram document. Context panels use ``details`` so they are
    expandable without relying on JavaScript.
    """
    events: list[str] = []
    cumulative_tokens = 0
    previous_timestamp: float | None = None

    for index, record in enumerate(trace, start=1):
        elapsed = "first step"
        if previous_timestamp is not None:
            elapsed = f"{(record.timestamp - previous_timestamp) * 1000:.1f} ms since previous step"
        previous_timestamp = record.timestamp
        cumulative_tokens += record.input_tokens + record.output_tokens

        messages = record.request.get("messages", [])
        message_count = len(messages) if isinstance(messages, list) else 0
        context = (
            '<details class="context">'
            f"<summary>Context window · {message_count} message{'s' if message_count != 1 else ''}</summary>"
            f'<pre class="json">{escape(_json(messages))}</pre>'
            "</details>"
        )
        request_payload = _payload("Exact request payload", record.request) + context
        events.append(
            _event(
                "api-call",
                f"API call · round {index}",
                f"Learner / Koan → LLM · {elapsed}",
                request_payload,
            )
        )
        response_payload = _payload("Exact response payload", record.response)
        events.append(
            _event(
                "api-response",
                f"API response · round {index}",
                (
                    f"LLM → Learner / Koan · {record.latency_ms:.1f} ms latency · "
                    f"{record.input_tokens} in · {record.output_tokens} out · "
                    f"{cumulative_tokens} cumulative"
                ),
                response_payload,
            )
        )
        events.append(_tool_events(record.tool_executions))

    empty = ""
    if not events:
        empty = '<p class="empty">No LLM interactions were recorded for this exercise.</p>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>llmSquire conversation trace</title>
<style>
:root {{ color-scheme: dark; --bg:#10141d; --panel:#19202d; --border:#344155; --text:#e8edf7; --muted:#9aa9c1; --blue:#68b5ff; --purple:#b792ff; --green:#63d9a5; --orange:#ffc36b; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--text); font:14px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
main {{ max-width:1180px; margin:auto; padding:28px 18px 56px; }} h1 {{ margin:0 0 6px; font-size:24px; }} .subtitle,.annotation {{ color:var(--muted); margin:0; }}
.lifelines {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin:28px 0 18px; }} .lifeline {{ text-align:center; border:1px solid var(--border); background:var(--panel); border-radius:8px 8px 0 0; padding:10px; font-weight:bold; }} .lifeline::after {{ content:""; display:block; border-left:2px dashed var(--border); height:38px; margin:10px auto -48px; width:0; }}
.event {{ display:grid; grid-template-columns:30% 70%; margin:14px 0; }} .arrow {{ position:relative; align-self:32px; height:2px; background:var(--blue); margin:18px 16px 0 0; }} .arrow::after {{ content:""; position:absolute; right:0; top:-5px; border-left:10px solid var(--blue); border-top:6px solid transparent; border-bottom:6px solid transparent; }} .api-response .arrow,.tool-result .arrow {{ background:var(--green); }} .api-response .arrow::after,.tool-result .arrow::after {{ border-left-color:var(--green); }} .tool-call .arrow {{ background:var(--purple); }} .tool-call .arrow::after {{ border-left-color:var(--purple); }}
.event-card {{ border:1px solid var(--border); border-left:4px solid var(--blue); border-radius:7px; background:var(--panel); padding:12px; min-width:0; }} .api-response .event-card,.tool-result .event-card {{ border-left-color:var(--green); }} .tool-call .event-card {{ border-left-color:var(--purple); }} h3,h4 {{ margin:0 0 4px; }} h4 {{ color:var(--orange); font-size:12px; }} .payload {{ margin-top:10px; }} pre {{ margin:5px 0 0; white-space:pre-wrap; overflow-wrap:anywhere; background:#0c1018; border:1px solid #263246; border-radius:5px; padding:10px; color:#d9e7ff; }} details {{ margin-top:10px; }} summary {{ cursor:pointer; color:var(--orange); }} .empty {{ border:1px dashed var(--border); border-radius:7px; padding:18px; color:var(--muted); }}
@media (max-width:650px) {{ .event {{ grid-template-columns:1fr; }} .arrow {{ display:none; }} .lifelines {{ font-size:11px; }} }}
</style>
</head>
<body><main>
<h1>LLM conversation sequence</h1><p class="subtitle">Exact API payloads, context growth, timing, and token use.</p>
<section class="lifelines" aria-label="Sequence diagram lifelines"><div class="lifeline">Learner / Koan</div><div class="lifeline">LLM</div><div class="lifeline">Tools</div></section>
{empty}<section class="events">{''.join(events)}</section>
</main>
<script>
// Payloads are already escaped server-side. This small inline enhancer makes
// JSON blocks keyboard-focusable without any external dependency.
document.querySelectorAll('pre.json').forEach(function (block) {{ block.tabIndex = 0; }});
</script>
</body></html>"""


def write_diagram(
    trace: Sequence[InteractionRecord],
    koan_name: str,
    test_name: str,
    output_dir: str | Path = "diagrams",
) -> Path:
    """Write a timestamped diagram file and return its path.

    Names are normalized for portable filenames while preserving the PRD naming
    convention: ``{koan}_{test}_{YYYYMMDD_HHMMSS}.html``.
    """
    def filename_part(value: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
        return normalized or "unnamed"

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = directory / f"{filename_part(koan_name)}_{filename_part(test_name)}_{timestamp}.html"
    path.write_text(render(trace), encoding="utf-8")
    return path


# Friendly aliases for callers that prefer a descriptive name.
generate_html = render
render_sequence_diagram = render
