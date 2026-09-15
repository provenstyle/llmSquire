# llmSquire

Koans for mastering LLM invocation, harness creation, skills, and evaluation-driven development.

## Quick Start

```bash
# Clone
git clone https://github.com/trayburn/llmSquire.git
cd llmSquire

# Install
pip install -e ".[dev]"

# Configure API
cp .env.example .env
# Edit .env with your API key (Fireworks or Ollama Cloud)

# Run the koans
python -m llmsquire
```

The runner stops at the first failing koan. Open the file it points you to, fill in the `_fill_` blanks, and run again.

## Sequence Diagrams

After each exercise, the runner prints a path to an HTML sequence diagram showing the exact LLM payloads, responses, tool calls, and context window at each round trip. Open it in any browser to see what the model actually saw.

## The Path

18 koans across 5 phases:

1. **Foundations** — invocation, statelessness, context window, system prompts
2. **Tool Calling** — definitions, the call-and-response loop, constraining tools, context composition
3. **Skills** — RTCC prompt structure, evaluation criteria
4. **EDD** — Red/Green/Refactor for prompts with majority-vote evaluation
5. **Decomposition** — workflows, guardrails, adversarial review, harness building, punch-out points

See [PRD.md](PRD.md) for the full product requirements document.

## License

MIT