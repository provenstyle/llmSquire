# llmSquire — Product Requirements Document

## A Koans-Style Learning Journey for Mastering LLM Invocation, Harness Creation, Skills, and Evaluation-Driven Development

---

## 1. Vision

llmSquire is a koans-style learning platform that teaches developers how to build effective LLM-powered workers through direct experience. It follows the tradition of Ruby Koans and Squire (C# Kihon): learners progress through a sequence of exercises, each one failing until they provide the correct implementation, with the test runner stopping at the first failure and guiding them to the exact file and line to meditate on.

The central thesis is that LLMs are stateless function callors whose power emerges from the tools we give them and the constraints we place around them. By the end of the journey, a learner will have internalized, through their own hands-on work:

- LLMs are stateless — every call is a fresh start, and context management is your job
- Tool calling is the primitive — interesting workers emerge from constraining what tools are available
- Evaluation-driven development (EDD) is how you know your worker actually works
- Complex workflows are decomposed into individually testable steps (Stage 3/4 lessons)
- Skills are written job descriptions for units of work — the prompt is the code

---

## 2. Influences and Precedents

### 2.1 Ruby Koans (spatten/ruby_koans)

Ruby Koans teaches the Ruby language through a sequence of test files (`about_basics.rb`, `about_arrays.rb`, `about_classes.rb`, etc.) managed by a runner called `path_to_enlightenment.rb`. The runner loads files in order, executes tests, and stops at the first failure with a zen-like message:

```
Thinking AboutAsserts
  test_assert_truth has damaged your karma.

You have not yet reached enlightenment ...
<false> is not true.

Please meditate on the following code:
./about_basics.rb:10:in `test_assert_truth'
```

Key design lessons for llmSquire:
- **Sequential disclosure**: Each koan builds on the last. The path is fixed. You cannot skip ahead.
- **Fill-in-the-blank**: Learners either replace `__` (double underscore) with the correct value, or implement a method body. The code they see is minimal and focused.
- **Stop at first failure**: The runner halts, points to the exact file and line, and offers a zen reflection. This creates a tight feedback loop.
- **The harness is invisible**: `edgecase.rb` contains the Sensei, the Koan base class, the test runner, and the zen output. Learners never need to read or understand it. They only see their koan files.
- **Culture through practice**: The README says "Testing is not just something we pay lip service to, but something we live." The koans teach TDD culture by making it the only way to progress.

### 2.2 Squire (ImprovingBootcamp/Squire)

Squire is the C#/.NET equivalent, originally built by Tim Rayburn and the Round Table community. It uses the "Kihon" pattern (Kihon = "basics" in Japanese martial arts):

- **Abstract base classes** (`StringKihonBase.cs`, `NumbersKihonBase.cs`, etc.) contain all test methods with Arrange/Act/Assert structure
- **Concrete derived classes** (`StringKihon.cs`, `NumbersKihon.cs`) contain only the method signatures with `throw new NotImplementedException()` — this is what the learner edits
- **Clean separation**: The learner opens `StringKihon.cs` and sees 14 method stubs. They implement one, run the tests, and move to the next. The grading infrastructure (NUnit, Rhino.Mocks, Castle.Windsor) is completely hidden in the Framework directory.
- **IoC container**: `BaseKihon` initializes a Windsor Castle container for each test, teaching dependency injection through osmosis.

Key design lessons for llmSquire:
- **The student file is decluttered**: Only method signatures and `throw new NotImplementedException()`. No test attributes, no arrange/act/assert, no mocking setup. Pure focus on the concept being taught.
- **The framework is isolated**: All grading infrastructure lives in a separate directory hierarchy the learner never needs to open.
- **Descriptive method names as curriculum**: `Convert_To_Uppercase`, `Combine_Parts_Of_A_Name`, `Determine_The_Position_Of_a_In_b` — the method names ARE the lesson plan.

### 2.3 Stage 3 & Stage 4 Certification (Improving IOS)

The Improving Intelligence Operating System certification framework defines the maturity model for AI capability. The lessons from Stage 3 and Stage 4 directly inform the llmSquire curriculum:

**Stage 3 (Task) lessons:**
- A "skill" is a written job description for a unit of work — the prompt IS the code
- Evaluation-Driven Development (EDD): write evaluation criteria first, then iterate on the prompt until it passes, then remove dead-weight instructions (load-bearing principle)
- RTCC structure: Role, Task, Context, Constraints — every prompt should have these
- Load-bearing principle: >90% of instructions should serve at least one evaluation criterion. Instructions that can be removed without causing any evaluation to fail are dead weight.
- Model tier awareness: mid-tier models should be sufficient. If you need a frontier model, your prompt is probably under-specified.

**Stage 4 (Workflow) lessons:**
- Complex workflows are chains of individually validated Stage 3 agents
- Guardrails sit BETWEEN steps, not inside them — they validate outputs before the next step begins
- Two complementary guardrail forms: adversarial review agents (LLM-based, different perspective) and deterministic hooks/sentinels (code-based, runtime validation)
- Punch-out points: explicit human decision points that cannot be bypassed
- End-to-end success rate: at 95% per-step accuracy, a 20-step pipeline succeeds only ~36% of the time. Compounding error is the enemy.
- Audit trails: every step must record model, tokens, cost, and be traceable to its origin
- The harness EXECUTES — a YAML config that documents step order is not a harness. If a human has to type the command for each step, the human IS the workflow.

---

## 3. Target Audience

- Developers who have used ChatGPT/Copilot but never built a deliberate LLM worker
- Developers who have written prompts but never evaluated them systematically
- Developers who want to build agentic workflows but don't know where to start
- Teams adopting AI who need a shared vocabulary and mental model
- Stage 3 certification candidates who need hands-on practice before submitting

**Prerequisite knowledge**: Basic Python. Familiarity with the concept of an API call. No machine learning background required.

---

## 4. Design Principles

### 4.1 The Student File Is Sacred

The single most important design rule, borrowed from both Ruby Koans and Squire:

> The code the learner sees should never be about the grading. It should be decluttered to focus exclusively on what they are supposed to be learning.

This means:
- Student files contain ONLY the exercise: a function signature, a prompt template, a tool definition, or a fill-in-the-blank
- No test attributes, no assertion imports, no mocking setup, no boilerplate
- No `if __name__ == "__main__"` blocks, no configuration
- Comments in student files are teaching comments — they explain the concept, not the infrastructure
- The grading harness lives in a separate package/directory that the learner never needs to open

### 4.2 Stop at First Failure

Following Ruby Koans: the runner executes exercises in order and stops at the first failure. The learner sees:

```
Thinking AboutStatelessness
  test_the_model_does_not_remember has damaged your karma.

You have not yet reached enlightenment ...
The model returned 'I don't have any previous context' but you expected it to remember the name 'Alice'.

Please meditate on the following code:
./koans/about_statelessness.py:23

mountains are merely mountains
```

This creates the tight, meditative feedback loop that makes koans effective.

### 4.3 Experience Before Theory

Each koan teaches through failure first. The learner encounters a surprising behavior (the model doesn't remember, the tool wasn't called, the output format is wrong), then they fix it. The explanation comes through the test name and the failure message, not through a lecture. Brief teaching comments in the student file provide just enough context to understand what they're looking at.

### 4.4 Real LLM Calls, Not Mocked Ones

Unlike traditional koans where the answer is deterministic, llmSquire exercises involve real LLM API calls. This is essential because the whole point is to experience the behaviors of actual stateless models. However:

- Exercises that test deterministic concepts (prompt structure, tool schema validation, output parsing) use local validation only — no API calls needed
- Exercises that test LLM behavior use real API calls but with fixed models, temperatures, and system prompts to make results reproducible enough to evaluate
- The harness includes retry logic and handles non-determinism gracefully (e.g., testing for the presence of a concept in the response rather than an exact string match)
- A `--offline` mode runs only the deterministic exercises, for environments without API access

### 4.5 Progressive Complexity

The journey moves from concrete to abstract, from single calls to composed workflows:

1. **Invocation** — calling an LLM, understanding the request/response cycle
2. **Statelessness** — experiencing the model's lack of memory firsthand
3. **Context Engineering** — managing what goes into the context window
4. **Tool Calling** — defining tools, seeing the model choose to call them
5. **Constraining Tools** — limiting available tools to shape worker behavior
6. **Context Composition** — seeing exactly what the model sees after tool calls, and why this changes everything about testing
7. **Skills** — writing structured prompts as job descriptions (RTCC)
8. **Evaluation** — writing criteria that determine if a skill actually works
9. **EDD** — iterating on a skill using evaluation feedback (Red/Green/Refactor)
10. **Decomposition** — breaking complex workflows into individually testable steps
11. **Guardrails** — adding validation between steps
12. **Orchestration** — wiring steps together with a harness that executes

### 4.6 Sequence Diagrams — Seeing the Conversation

LLM interactions are multi-round-trip conversations that happen inside a black box. The learner writes `llm.ask(messages=[...])` and gets back a response, but they cannot see the intermediate steps: the tool calls the model requested, the tool results the harness returned, the second LLM call that incorporated those results, or the exact payload that was sent on the second trip. This invisibility is a major pedagogical barrier.

Every time a koan exercise triggers one or more LLM interactions, the runner automatically produces a single-file HTML sequence diagram that renders the complete conversation as a visual timeline. The diagram shows:

- **Every LLM API call** as a vertical lifeline with the exact request payload (messages array, tools, system prompt, model, temperature) and the exact response (content, tool_calls, usage, latency in milliseconds)
- **Every tool invocation** as an arrow between the harness lifeline and the tool lifeline, showing the tool name, arguments, return value, and execution time
- **The growing context window** as an expandable panel on the LLM lifeline — at each round trip, the learner can see exactly what messages are in context, including system prompt, prior user messages, assistant responses, tool calls, and tool results
- **Timings** between every step, making latency and multi-round-trip cost visible
- **Token counts** per call (input tokens, output tokens, cumulative tokens) so the cost of context growth is concrete

This is not a debugging tool. It is a teaching instrument. Visual learners need to see that when a model calls a `read_file` tool, the file contents come back as a `tool` role message in the context, and on the next round trip the model sees those contents alongside everything else. Once you can see that, a critical insight becomes obvious: for evaluation purposes, you don't need to actually read files from disk — you can pre-populate the context window with the file contents as if the tool had already been called. This insight is the bridge between understanding tool calling and doing effective EDD.

The HTML files are self-contained (inline CSS and JS, no external dependencies) and are written to a `diagrams/` directory next to the koans. The runner prints the file path after each exercise. Learners can open them in any browser.

---

## 5. Architecture

### 5.1 Project Structure

```
llmSquire/
├── PRD.md                          # This document
├── README.md                       # Getting started guide
├── pyproject.toml                  # Package config, dependencies
├── llmsquire/                      # The harness (learners don't touch this)
│   ├── __init__.py
│   ├── sensei.py                   # Test runner — stops at first failure, zen output
│   ├── koan.py                     # Base Koan class, exercise registration
│   ├── llm_client.py               # LLM API client wrapper (OpenAI-compatible)
│   ├── evaluator.py                # Evaluation framework for LLM-based exercises
│   ├── assertions.py               # Custom assertions for LLM responses
│   ├── diagram.py                  # Sequence diagram generator (single-file HTML)
│   └── path_to_enlightenment.py    # Ordered list of koan modules
├── koans/                          # The exercises (learners edit these)
│   ├── about_invocation.py
│   ├── about_statelessness.py
│   ├── about_context_window.py
│   ├── about_system_prompts.py
│   ├── about_tool_definitions.py
│   ├── about_tool_calling.py
│   ├── about_constraining_tools.py
│   ├── about_context_composition.py
│   ├── about_skills_rtcc.py
│   ├── about_evaluation_criteria.py
│   ├── about_edd_cycle.py
│   ├── about_decomposition.py
│   ├── about_guardrails.py
│   ├── about_adversarial_review.py
│   ├── about_orchestration.py
│   └── about_punch_out.py
├── diagrams/                       # Auto-generated sequence diagrams (HTML)
│   └── .gitkeep
├── solutions/                      # Reference solutions (for self-checking)
│   ├── about_invocation.py
│   └── ...
├── evals/                          # Evaluation configs for the koans themselves
│   └── promptfooconfig.yaml
├── tests/                          # Tests for the harness itself
│   └── test_sensei.py
└── .env.example                    # API key configuration template
```

### 5.2 The Student Experience

A learner opens `koans/about_statelessness.py` and sees:

```python
# Lesson: LLMs are stateless. Every call is a fresh start.
#
# You will make two separate calls to the model.
# In the first call, you tell it your name.
# In the second call, you ask it what your name is.
#
# The test will check whether the model remembers your name
# across the two calls. Think about what you expect to happen.

from llmsquire import Koan, llm

class AboutStatelessness(Koan):

    def test_the_model_does_not_remember(self):
        # Step 1: Tell the model your name
        first_response = llm.ask(
            messages=[
                {"role": "user", "content": "My name is Alice."}
            ]
        )

        # Step 2: Ask the model what your name is — in a SEPARATE call
        second_response = llm.ask(
            messages=[
                {"role": "user", "content": "What is my name?"}
            ]
        )

        # What do you expect the model to say?
        # Replace the line below with your assertion about second_response
        self.assert_match("Alice", second_response)
```

The learner runs `python -m llmsquire` and sees:

```
Thinking AboutStatelessness
  test_the_model_does_not_remember has damaged your karma.

You have not yet reached enlightenment ...
Expected 'Alice' in response, but model said: 'I don't have any previous context...'

The model has no memory between calls. Each call is independent.
To make the model "remember," you must pass the previous conversation
in the messages array of the second call.

Please meditate on the following code:
./koans/about_statelessness.py:28

Sequence diagram: diagrams/about_statelessness_test_the_model_does_not_remember_20260914_153022.html

mountains are merely mountains
```

The learner can open the sequence diagram in their browser to see exactly what was sent to the LLM on each call, what came back, and how the context window differed between the two calls. For this koan, the diagram makes the statelessness viscerally visible: the second call's context panel shows only the single "What is my name?" message — no memory of "Alice" anywhere in the payload.

The learner edits the file, re-runs, and progresses. The grading logic (the assertion, the failure message, the zen output) all live in `llmsquire/sensei.py` and `llmsquire/assertions.py` — the learner never sees them.

### 5.3 The Harness: Sensei and Koan

Following Ruby Koans' `edgecase.rb`:

**`llmsquire/koan.py`** — Base class that exercises inherit from. Provides:
- `self.assert_match(expected, actual)` — substring/pattern match for LLM responses
- `self.assert_tool_called(response, tool_name)` — verifies a tool was invoked
- `self.assert_tool_not_called(response, tool_name)` — verifies a tool was NOT invoked
- `self.assert_json_schema(response, schema)` — validates structured output
- `self.assert_eval(response, criteria)` — runs an LLM-based evaluation
- `llm.ask(messages=..., tools=..., model=...)` — the LLM client wrapper (records all round trips to a conversation trace)
- After each test method completes (or fails), the harness automatically calls `diagram.render(trace)` to produce the HTML sequence diagram

**`llmsquire/sensei.py`** — The runner. Discovers all Koan subclasses, runs them in path order, stops at first failure, prints zen messages. Modeled directly on Ruby Koans' Sensei class.

**`llmsquire/path_to_enlightenment.py`** — The ordered list of koan modules. This IS the curriculum:

```python
PATH = [
    "koans.about_invocation",
    "koans.about_statelessness",
    "koans.about_context_window",
    "koans.about_system_prompts",
    "koans.about_tool_definitions",
    "koans.about_tool_calling",
    "koans.about_constraining_tools",
    "koans.about_context_composition",
    "koans.about_skills_rtcc",
    "koans.about_evaluation_criteria",
    "koans.about_edd_cycle",
    "koans.about_decomposition",
    "koans.about_guardrails",
    "koans.about_adversarial_review",
    "koans.about_orchestration",
    "koans.about_punch_out",
]
```

### 5.4 LLM Client Wrapper

The `llm.ask()` function is the single entry point for all LLM interactions. It wraps an OpenAI-compatible API client and:

- Uses a fixed model (configurable via `.env`, defaulting to a mid-tier model)
- Sets temperature to 0 for reproducibility where possible
- Accepts `messages`, `tools`, `model`, and `temperature` parameters
- Returns a structured response object with `.content`, `.tool_calls`, and `.usage`
- Handles API errors gracefully with clear messages
- Logs all calls for the audit trail (teaching Stage 4 habits from day one)
- **Records every round trip** — each call captures the full request payload, full response, timestamp, latency, and token usage into a conversation trace that the diagram generator consumes after the exercise completes

The client maintains a per-exercise conversation trace (a list of interaction records) that is reset at the start of each koan test method. When a test involves the full tool-call loop (user → model → tool_call → tool_result → model → final_answer), the trace captures all round trips, not just the initial call. This trace is what makes the sequence diagrams possible and what makes the audit trail in later koans a natural extension of behavior the learner has been seeing since koan 1.

### 5.5 Sequence Diagram Generator

**`llmsquire/diagram.py`** consumes the conversation trace from an exercise and produces a single-file HTML sequence diagram. The design goals are:

1. **Self-contained**: All CSS and JS is inline. No external dependencies, no CDN links, no web font requirements. The file opens in any browser, on any machine, even offline.

2. **Faithful to the actual payloads**: The diagram shows the exact JSON that was sent to the API and the exact JSON that came back. Messages are rendered with syntax highlighting (via a small inline highlighter, not a library). Tool call arguments and tool results are shown in full, not summarized. If the learner sent 4,000 tokens of context, the diagram shows 4,000 tokens of context — collapsible, but complete.

3. **Lifeline layout**: Three vertical lifelines — Learner/Koan (left), LLM (center), Tools (right). Arrows between them represent the direction of communication:
   - Learner → LLM: API call (shows request payload)
   - LLM → Learner: API response (shows response payload, tool_calls, usage, latency)
   - LLM → Tools: tool call request (shows tool name + arguments)
   - Tools → LLM: tool result (shows return value, execution time) — delivered as a `tool` role message on the next round trip

4. **Context window panel**: At each LLM lifeline position, an expandable panel shows the complete messages array as it existed at that point in the conversation. This is the key pedagogical feature: the learner can see that after a `read_file` tool call, the context window now contains the system prompt + the user's original message + the assistant's tool_call response + the tool result message with the file contents. The context grows with every round trip, and the panel makes that growth visible, tangible, and concrete.

5. **Timing and token annotations**: Each arrow is annotated with elapsed time (milliseconds between this step and the previous). Each LLM response is annotated with input tokens, output tokens, and cumulative tokens for the exercise. This makes the cost of multi-round-trip patterns viscerally clear.

6. **Diagram file naming**: `diagrams/{koan_name}_{test_name}_{timestamp}.html`. The runner prints the path after each exercise:
   ```
   Sequence diagram: diagrams/about_tool_calling_test_the_full_loop_20260914_153022.html
   ```

7. **Diagram on failure**: When a test fails, the diagram is still generated for the interactions that occurred before the failure. The learner can examine what the model actually did, what context it had, and why the assertion failed. This is often more educational than the failure message itself — seeing that the model called the wrong tool, or didn't call any tool, or produced output in the wrong format is immediately diagnosable from the diagram.

---

## 6. Curriculum — The Path to Enlightenment

### Phase 1: Foundations of LLM Invocation

#### Koan 1: about_invocation.py — "The First Call"

**Concept**: An LLM is a function that takes text and returns text. You call it through an API.

**Exercises**:
- Make your first LLM call using `llm.ask(messages=[...])`
- Understand the message format: role ("user"/"assistant"/"system") and content
- See that the response is a structured object with `.content`
- Fill in `__` values: what is the role of each message? What does `.content` contain?

**Student sees**: Clean function calls with `__` blanks to fill in. No API configuration, no error handling, no imports beyond `llm`.

#### Koan 2: about_statelessness.py — "The River You Cannot Step In Twice"

**Concept**: Every LLM call is independent. The model has no memory of previous calls.

**Exercises**:
- Call the model twice. Tell it your name in call 1. Ask for it in call 2. Experience that it doesn't remember.
- Fix it by passing the conversation history in the messages array of call 2.
- Call the model with a long conversation history. Observe that it "remembers" — but only because YOU provided the memory.
- Reflection comment: "The model doesn't remember. YOU remember, and you pass that memory forward."

**Key insight**: Statelessness is not a bug — it's a design constraint that makes LLMs composable and predictable.

#### Koan 3: about_context_window.py — "The Edge of Memory"

**Concept**: The context window is finite. You must choose what goes in it.

**Exercises**:
- Build a conversation with 20 messages. See it works fine.
- Build a conversation with 200 messages. Observe truncation or errors.
- Write a function that trims conversation history to the last N messages.
- Discover that what you leave OUT of the context is as important as what you put IN.

#### Koan 4: about_system_prompts.py — "Setting the Stage"

**Concept**: The system prompt sets the model's role, behavior, and constraints.

**Exercises**:
- Call the model without a system prompt. Ask it to be a pirate. It's reluctantly pirate-y.
- Call the model WITH a system prompt: "You are a pirate." Ask it anything. It's fully pirate-y.
- Add constraints to the system prompt: "You are a pirate who only speaks in 3-word sentences."
- Observe that the system prompt is the foundation of the RTCC framework (Role, Task, Context, Constraints).

---

### Phase 2: Tool Calling — The Core Primitive

#### Koan 5: about_tool_definitions.py — "Giving the Model Hands"

**Concept**: Tools are the bridge between the LLM's text reasoning and the real world.

**Exercises**:
- Define a simple tool (a calculator) using the JSON tool schema
- Call the model with the tool available. Ask it "What is 2+2?" and see it choose to call the tool.
- Examine the structured `tool_calls` in the response
- Fill in `__` blanks in a tool definition schema

**Student sees**: A clean tool definition with blanks to fill in (name, description, parameters). The schema is the lesson.

#### Koan 6: about_tool_calling.py — "The Call and Response"

**Concept**: Tool calling is a multi-turn dance: the model requests a tool call, you execute it, you return the result, the model continues.

**Exercises**:
- Send a message that triggers a tool call
- Extract the tool name and arguments from the response
- Execute the tool function (provided for you) and get the result
- Send the tool result back to the model as a `tool` role message
- Get the model's final response incorporating the tool result
- Experience the full loop: user → model → tool_call → tool_result → model → final_answer

**Key insight**: The LLM doesn't execute tools. YOU execute tools. The LLM only decides which tools to call and with what arguments.

#### Koan 7: about_constraining_tools.py — "The Power of No"

**Concept**: What you DON'T give the model is as important as what you do. Constraining available tools shapes worker behavior.

**Exercises**:
- Give the model 5 tools. Ask it to "calculate the square root of 16 and then write it to a file." See it call both the calculator and the file writer.
- Now give it ONLY the calculator tool. Ask the same question. See it calculate but explain it can't write the file.
- Give a model ONLY a "search" tool. Ask it to "summarize this article." See it struggle — it doesn't have a summarize tool.
- Give a different model a "summarize" tool. Ask the same question. See it use the tool.
- Reflection: "A worker is defined by its tools. Change the tools, change the worker."

**Key insight**: This is the foundational lesson. By constraining tools, you define what a worker CAN do and, critically, what it CANNOT do. This is how you build specialized workers rather than general-purpose chatbots.

#### Koan 8: about_context_composition.py — "What the Model Actually Sees"

**Concept**: After a tool call, the context window grows. The model's next response is based on everything in context — the system prompt, the user's message, the assistant's tool call, and the tool result. Understanding exactly what is in context at each step is the key to effective evaluation.

**Exercises**:
- Trigger a `read_file` tool call. Open the sequence diagram. See the context window panel at round trip 1 (before the tool call) vs. round trip 2 (after the tool result was added). The file contents are now in context as a `tool` role message.
- Trigger two tool calls in sequence (read_file, then search). See how the context grows with each round trip. The model sees all prior tool results, not just the most recent one.
- Now, instead of triggering a real tool call, construct the messages array manually: include the system prompt, a user message, a synthetic assistant tool_call message, and a synthetic tool result message with the file contents pre-filled. Call the model with this pre-populated context. Observe that the model responds exactly as if it had called the tool itself.
- Reflection comment: "The model doesn't know or care whether a tool was actually called. It only sees the messages in its context window. If you put the tool result there, it's there. This means you can test skills that use tools WITHOUT actually running the tools — you just construct the context the skill would have seen."

**Key insight**: This is the bridge between tool calling and EDD. If a skill reads three files and then reasons about them, you don't need your EDD runner to put files on disk, configure paths, and execute the read_file tool. You construct the test scenario by pre-populating the context window with the messages the skill would have produced — the tool calls and tool results — and then you evaluate the model's reasoning output directly. The sequence diagram from the previous koan showed you exactly what those messages look like; now you use that knowledge to build tests.

**Sequence diagram focus**: This koan's diagram is the most important one in the curriculum. It shows two scenarios side by side: (1) the real tool-call loop with actual file reads, and (2) the synthetic context with pre-populated tool results. The diagrams are visually identical in structure — the same message types, the same roles, the same content. This visual equivalence is the "aha" moment: the model cannot distinguish between real tool calls and synthetic ones, so your tests don't need to either.

**Student sees**: A messages array with blanks to fill in, where the learner constructs a synthetic conversation that includes tool call and tool result messages. The teaching comments explain why this works and what it enables.

---

### Phase 3: Skills — Prompts as Code

#### Koan 9: about_skills_rtcc.py — "The Job Description"

**Concept**: A skill is a written job description for a unit of work. The RTCC framework (Role, Task, Context, Constraints) provides the structure.

**Exercises**:
- Read a poorly-structured prompt and see its output is unpredictable
- Rewrite it using RTCC: define the Role, the Task, the Context, the Constraints
- See how the structured version produces more consistent output
- Fill in the missing RTCC sections in a partially-written skill
- Write a complete skill from scratch for a specific task (e.g., "Extract action items from meeting notes")

**Student sees**: A prompt template with RTCC section headers and blanks to fill in. Like a form to complete.

**Stage 3 connection**: This is exactly what Stage 3 certification requires — a deliberate, structured prompt with clear constraints. The learner is practicing the artifact they'll need to certify.

#### Koan 10: about_evaluation_criteria.py — "How Do You Know It Works?"

**Concept**: A skill without evaluation is an opinion. Evaluation criteria make it engineering.

**Exercises**:
- Run a skill 5 times and observe output variation (even at temperature 0, there's some)
- Write 3 evaluation criteria for the "extract action items" skill (e.g., "all action items must have an owner", "no non-action sentences included", "output must be valid JSON")
- See how criteria transform subjective "looks good" into objective pass/fail
- Run the skill against test inputs and score with the criteria
- Reflection: "If you can't evaluate it, you can't improve it. If you can't improve it, you're just hoping."

**Stage 3 connection**: Stage 3 requires at least 3 evaluation criteria. The learner is building the evaluation artifact.

---

### Phase 4: Evaluation-Driven Development (EDD)

#### Koan 11: about_edd_cycle.py — "Red, Green, Refactor for Prompts"

**Concept**: EDD applies TDD discipline to prompt engineering. Write criteria first (Red), iterate until passing (Green), remove dead-weight instructions (Refactor).

**Exercises**:
- Start with a weak skill and a set of evaluation criteria. Run it. See it fail (Red).
- Make one change to the skill prompt. Re-run. See the score change.
- Iterate 3 times, documenting each hypothesis and result in an iteration log
- Once all criteria pass (Green), review the prompt for load-bearing: can any instruction be removed without causing a criterion to fail? Remove dead weight (Refactor).
- Calculate the load-bearing percentage: what fraction of instructions serve at least one evaluation criterion?
- **Context-window testing exercise**: The skill under test reads three files and reasons about them to produce a summary. Instead of creating real files on disk and running the read_file tool, construct the test scenario by pre-populating the messages array with synthetic tool call and tool result messages containing the file contents. Run the skill against this synthetic context. Observe that the evaluation works identically — the model produces the same quality of reasoning whether the file contents came from real tool calls or from synthetic messages you constructed.
- Open the sequence diagram from the context-composition koan (Koan 8) side by side with this exercise's diagram. See that the message structure is the same. This is the practical payoff of understanding context composition: your EDD runner becomes simpler, faster, and more deterministic because you eliminate file I/O and tool execution from the test loop.

**Stage 3 connection**: This IS Stage 3. The learner is doing the exact Red/Green/Refactor cycle that certification requires, with the iteration log and load-bearing analysis. The context-window testing exercise directly addresses a common failure mode in Stage 3 submissions: practitioners who try to evaluate skills that use tools by setting up complex file fixtures and running the full tool-call loop, when they could simply construct the context the skill would have seen and evaluate the reasoning output directly.

**Student sees**: A skill file, an evaluation file, and an iteration log template. They edit the skill, run the eval, log the iteration, and repeat. The harness runs the evaluation and reports scores. The context-window testing exercise provides a pre-built messages array template with blanks for the synthetic tool results.

---

### Phase 5: Decomposition — From Tasks to Workflows

#### Koan 12: about_decomposition.py — "Divide and Conquer"

**Concept**: Complex workflows are chains of individually validated skills. Each step does one thing well.

**Exercises**:
- Given a complex task ("Research a topic, summarize findings, and draft an email report"), identify that no single skill can do this well
- Break it into 3 steps: research, summarize, draft email
- Write evaluation criteria for EACH step independently
- Verify that each step passes its own evaluation at 95%+ before composing them
- Run the 3 steps in sequence, passing outputs as inputs
- Observe: each step is a Stage 3 agent. The composition is the beginning of Stage 4.

**Stage 4 connection**: Stage 4 requires multiple Stage 3 agents wired into a workflow. The learner is building the first workflow and understanding why each step must be individually validated first.

#### Koan 13: about_guardrails.py — "The Walls Between Rooms"

**Concept**: Guardrails sit BETWEEN steps, not inside them. They validate outputs before the next step is allowed to begin.

**Exercises**:
- Run the 3-step workflow from the previous koan without guardrails. Inject a bad input. See the error propagate.
- Add a deterministic guardrail (a Python function) between step 1 and step 2: validate that the research output is non-empty and contains at least 3 findings.
- See the guardrail catch the bad input and halt the workflow
- Add another guardrail between step 2 and step 3: validate the summary is under 500 words and contains no PII patterns
- Reflection: "Guardrails are infrastructure, not UX. They must be automated — human review between steps is Stage 2, not Stage 4."

**Stage 4 connection**: Stage 4 requires both deterministic hooks AND adversarial review agents. This koan introduces the deterministic side.

#### Koan 14: about_adversarial_review.py — "The Red Team"

**Concept**: Adversarial review agents challenge the prior step's output from a DIFFERENT perspective. They are not redundant second opinions — they are trying to find what went wrong.

**Exercises**:
- Write an adversarial agent that reviews the research step's output for factual claims without sources
- Give it a DIFFERENT prompt, a DIFFERENT role, and an explicitly adversarial posture
- Run the adversarial agent on good output — it finds nothing concerning
- Run the adversarial agent on output with planted errors — it catches them
- Contrast with a "verification" agent that just re-checks the same criteria — see how it misses things the adversarial agent catches
- Reflection: "An adversarial agent has a distinct lens, its own prompt, and an explicitly adversarial posture. It is trying to find what went wrong, not validate what went right."

**Stage 4 connection**: This is the exact Stage 4 requirement — adversarial agents must genuinely challenge with a different perspective, not just re-verify.

#### Koan 15: about_orchestration.py — "The Harness Executes"

**Concept**: A harness is a script that EXECUTES the workflow end-to-end: calls agents in sequence, passes outputs, fires guardrails, handles failures. A YAML config that documents step order is NOT a harness.

**Exercises**:
- Write a Python harness that runs the 3-step workflow with guardrails
- The harness must: call step 1, run guardrail 1, call step 2, run guardrail 2, call step 3, produce final output
- Add failure handling: if a guardrail fails, retry the step once, then halt with an error
- Add audit logging: each step records model, input tokens, output tokens, and cost
- Run the harness end-to-end and verify it produces correct output
- Run it with a bad input and verify it halts at the appropriate guardrail
- Reflection: "If a human has to type the command for each step, the human IS the workflow."

**Stage 4 connection**: The harness/runner script is a hard Stage 4 requirement. This koan teaches it directly.

#### Koan 16: about_punch_out.py — "The Human in the Machine"

**Concept**: Punch-out points are explicit, provable human evacuation points where the workflow cannot proceed without human sign-off.

**Exercises**:
- Add a punch-out point to the workflow: after the research step, a human must approve the findings before summarization begins
- Implement the punch-out as a checkpoint that returns a "pending approval" status
- Test the bypass: attempt to proceed without approval. The harness must block it.
- Test the approval: simulate human approval. The harness proceeds.
- Document the punch-out point: what triggers it, what the human decides, how it's enforced
- Reflection: "Punch-out points must have been actively tested for bypass. Points that exist on paper but have never been tested are a red signal."

**Stage 4 connection**: Stage 4 requires documented, tested punch-out points. This koan is the capstone.

---

## 7. The Decluttered Editing Experience

### 7.1 What the Learner Opens

When a learner works on `koans/about_constraining_tools.py`, they see ONLY:

```python
# Lesson: A worker is defined by its tools.
# Change the tools, change the worker.
#
# In this exercise, you have a calculator tool and a file_writer tool.
# The model needs to calculate 2+2 and write the result to a file.
#
# First, give the model BOTH tools and see it do both.
# Then, give the model ONLY the calculator and observe what happens.

from llmsquire import Koan, llm

CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform arithmetic calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
            },
            "required": ["expression"]
        }
    }
}

FILE_WRITER_TOOL = {
    # Define the file_writer tool here
    # It should accept a filename and content
    __
}


class AboutConstrainingTools(Koan):

    def test_with_both_tools(self):
        response = llm.ask(
            messages=[{"role": "user", "content": "Calculate 2+2 and write the result to result.txt"}],
            tools=[CALCULATOR_TOOL, FILE_WRITER_TOOL]
        )
        # The model should call both tools
        self.assert_tool_called(response, "calculator")
        self.assert_tool_called(response, "file_writer")

    def test_with_calculator_only(self):
        response = llm.ask(
            messages=[{"role": "user", "content": "Calculate 2+2 and write the result to result.txt"}],
            tools=[__]  # Give the model ONLY the calculator
        )
        # The model should call the calculator but NOT the file_writer
        self.assert_tool_called(response, "calculator")
        self.assert_tool_not_called(response, "file_writer")
```

### 7.2 What the Learner Never Sees

The assertion logic, the LLM client configuration, the retry handling, the zen output formatting, the test discovery, the path ordering — all of that lives in `llmsquire/` and is never opened by the learner. They don't need to understand how `assert_tool_called` works. They just need to know it exists and what it checks.

This is the Squire pattern: `ConsoleKihon.cs` has 4 method stubs. `ConsoleKihonBase.cs` has 4 test methods with Rhino.Mocks setup. The learner opens `ConsoleKihon.cs`. The framework is invisible.

### 7.3 File Layout Convention

Every koan file follows this structure:

1. **Teaching comment** (top of file): 3-10 lines explaining the concept and what the learner will do
2. **Imports**: Only `from llmsquire import Koan, llm` (and occasionally pre-defined constants)
3. **Pre-defined constants**: Tool definitions, sample data, etc. — provided so the learner doesn't have to write boilerplate
4. **Koan class**: Contains test methods with `__` blanks or method bodies to implement
5. **Nothing else**: No `if __name__`, no configuration, no helper functions (those go in the harness)

---

## 8. Technical Decisions

### 8.1 Language: Python

Python is the lingua franca of AI/ML. It has the lowest barrier to entry for the target audience. The OpenAI Python SDK (and compatible clients) is the standard interface for LLM APIs.

### 8.2 LLM API: OpenAI-Compatible

The `llm.ask()` wrapper uses the OpenAI Python SDK with a configurable base URL. This means it works with:
- OpenAI (GPT models)
- Anthropic (via their OpenAI-compatible endpoint)
- Local models via Ollama, llama.cpp, vLLM
- Any OpenAI-compatible proxy (Bifrost, LiteLLM, etc.)

This keeps the koans provider-agnostic and lets learners use whatever API access they have.

### 8.3 Default Model: Mid-Tier

Following the Stage 3 principle that mid-tier models should be sufficient, the default model is a mid-tier option (e.g., GPT-4o-mini, Claude Haiku, or equivalent). The `.env.example` file documents how to change this. If a learner needs a frontier model to pass a koan, that's a bug in the koan, not a limitation of the learner.

### 8.4 Evaluation Framework

For koans that require LLM-based evaluation (e.g., "is this summary coherent?"), the harness includes a lightweight evaluator that calls a separate LLM with a rubric. This mirrors the Stage 3 certification approach where Claude Haiku acts as the examiner.

For koans that can be evaluated deterministically (e.g., "does the response contain valid JSON?", "was the calculator tool called?"), the harness uses pure Python assertions. Deterministic evaluation is preferred wherever possible — this is a Stage 4 lesson (deterministic hooks over LLM judges where feasible).

### 8.5 Non-Determinism Handling

LLM outputs are non-deterministic. The harness handles this by:
- Using temperature=0 by default for reproducibility
- Testing for semantic properties rather than exact strings (e.g., "response contains a number that equals 4" rather than "response equals '4'")
- Providing retry logic for flaky evaluations (3 attempts with majority vote)
- Using structured outputs (JSON mode) wherever possible to enable deterministic validation
- Accepting that some exercises will occasionally fail due to model variance — the learner re-runs and moves on

### 8.6 Offline Mode

A `--offline` flag runs only koans that don't require API calls (prompt structure, tool schema validation, output parsing, decomposition planning). This enables use in classrooms or environments without API access.

---

## 9. Metrics for Success

### 9.1 Learning Outcomes

A learner who completes all 16 koans should be able to:
1. Explain why LLMs are stateless and demonstrate how to manage conversation state
2. Define a tool using the JSON schema and handle the tool-call loop
3. Explain how constraining available tools shapes worker behavior
4. Read a sequence diagram of an LLM interaction and identify exactly what is in the context window at each round trip
5. Construct synthetic context windows with pre-populated tool results to test skills without executing real tool calls or file I/O
6. Write a skill using the RTCC framework
7. Write 3+ evaluation criteria for a skill
8. Run the EDD Red/Green/Refactor cycle on a skill, including context-window-based testing
9. Decompose a complex task into individually validated steps
10. Add deterministic guardrails between workflow steps
11. Write an adversarial review agent with a distinct perspective
12. Build a harness that executes a multi-step workflow end-to-end
13. Implement and test a punch-out point for human approval

### 9.2 Stage 3 Readiness

After completing Phase 4 (EDD), a learner has practiced all three Stage 3 artifacts:
- The Prompt (RTCC-structured skill)
- The Evaluations (3+ criteria with pass/fail thresholds)
- The Log (iteration log with hypothesis-driven changes)

They should be ready to create a Stage 3 certification submission.

### 9.3 Stage 4 Readiness

After completing Phase 5 (Decomposition), a learner has practiced all five Stage 4 artifacts:
- The Workflow Definition (decomposed steps)
- The Guardrails (deterministic + adversarial)
- The Punch-Out Evidence (tested bypass attempts)
- The End-to-End Success Rate (audit logging)
- The Audit Trail (per-step model/token/cost data)

They should understand what Stage 4 requires, though full Stage 4 certification requires real-world workflow deployment.

---

## 10. Future Phases (Post-MVP)

### 10.1 Community Koans

A mechanism for community-contributed koans, following the Ruby Koans model where the path_to_enlightenment can be extended. Each contribution must include the student file, the harness tests, and a brief teaching rationale.

### 10.2 Skill Library

A library of pre-built skills that learners can use as reference implementations or starting points for their own work. Each skill includes its RTCC prompt, evaluation criteria, and iteration log — serving as Stage 3 exemplars.

### 10.3 Visual Workflow Builder

A visual tool for composing multi-step workflows, where learners drag-and-drop skills into a pipeline and configure guardrails between them. This would generate the harness code automatically.

### 10.4 Multi-Language Support

Following Squire's example of having both NUnit and MSTest versions of the same kihon, llmSquire could support multiple LLM SDKs (OpenAI Python, LangChain, Anthropic SDK, etc.) as alternative "styles" of the same exercises.

### 10.5 Instructor Dashboard

A dashboard for instructors running llmSquire in a classroom setting, showing learner progress, common failure points, and time-to-complete per koan.

---

## 11. Open Questions

1. **API cost management**: Should we provide a hosted API key for learners, or require them to bring their own? A hosted key lowers the barrier but creates cost. A BYOK approach is more educational but may exclude some learners.

2. **Model-specific behavior**: Different models handle tool calling differently (e.g., some models are more aggressive about calling tools, others more reluctant). Should koans be tested against multiple models, or should we pin a single default? Recommendation: pin a default, document known differences in a compatibility matrix.

3. **Evaluation reliability**: LLM-based evaluation is itself non-deterministic. For the EDD koan specifically, how do we ensure the evaluation the learner writes is reliable enough to be educational? Recommendation: use structured output evaluation (JSON rubrics) rather than free-form LLM judging.

4. **Progress persistence**: Should the harness remember which koans the learner has passed (like a save file)? Ruby Koans doesn't — you just run from the top each time. Recommendation: follow Ruby Koans. Simplicity over convenience.

5. **Git integration**: Should learners commit their solutions? This teaches good habits but adds complexity. Recommendation: the README suggests committing after each koan, but the harness doesn't enforce it.

---

## 12. Naming and Branding

**llmSquire** — A squire is a knight in training. The learner is the squire, mastering the tools of the trade before becoming a knight (a certified Stage 3/4 practitioner). The name echoes "Squire," the C# koans project, creating a lineage.

The zen language from Ruby Koans ("damaged your karma," "expanded your awareness," "mountains are merely mountains") carries forward, adapted for the LLM domain. Instead of Ruby enlightenment, the learner seeks "LLM enlightenment" — the moment when statelessness, tool calling, and evaluation become instinctive rather than surprising.

---

## 13. License

MIT (matching the permissive spirit of both Ruby Koans and the educational goals of the project).

---

## Appendix A: Ruby Koans Design Patterns Applied

| Ruby Koans Pattern | llmSquire Application |
|---|---|
| `path_to_enlightenment.rb` (ordered file list) | `path_to_enlightenment.py` (ordered module list) |
| `edgecase.rb` (Sensei + Koan base) | `sensei.py` + `koan.py` (harness package) |
| `__` fill-in-the-blank | `__` fill-in-the-blank (same convention) |
| Stop at first failure + zen message | Stop at first failure + LLM-themed zen message |
| `test_assert_truth` (first koan) | `test_the_first_call` (first koan) |
| "has damaged your karma" / "expanded your awareness" | Same language, retained for cultural continuity |
| `rake` to run | `python -m llmsquire` to run |

## Appendix B: Squire Design Patterns Applied

| Squire Pattern | llmSquire Application |
|---|---|
| Abstract base class with test methods | Koan base class with test methods (hidden in harness) |
| Concrete class with `throw new NotImplementedException()` | Koan subclass with `__` blanks or `pass` stubs |
| `BaseKihon` with Castle.Windsor IoC | `Koan` with LLM client and assertion helpers |
| Framework/ directory isolates grading | `llmsquire/` package isolates grading |
| Descriptive method names as curriculum | Descriptive test names as curriculum |
| Student never opens Framework/ | Student never opens llmsquire/ |
| Kihon = "basics" in martial arts | Squire = knight-in-training; progression toward mastery |

## Appendix C: Stage 3/4 Assessment Principles Applied

| Stage 3/4 Principle | llmSquire Koan |
|---|---|
| LLMs are stateless function callors | about_statelessness |
| Tool calling is the core primitive | about_tool_definitions, about_tool_calling |
| Constraining tools defines workers | about_constraining_tools |
| Context composition after tool calls | about_context_composition |
| Sequence diagrams make round trips visible | All koans (auto-generated by diagram.py) |
| Synthetic context enables tool-free testing | about_context_composition, about_edd_cycle |
| RTCC prompt structure | about_skills_rtcc |
| 3+ evaluation criteria required | about_evaluation_criteria |
| EDD Red/Green/Refactor | about_edd_cycle |
| Load-bearing principle | about_edd_cycle (Refactor phase) |
| Decompose into individually validated steps | about_decomposition |
| Guardrails between steps, not inside | about_guardrails |
| Adversarial agents with distinct perspective | about_adversarial_review |
| Harness EXECUTES, doesn't just document | about_orchestration |
| Punch-out points tested for bypass | about_punch_out |
| Per-step model/token/cost audit trail | about_orchestration (audit logging) |
| End-to-end success rate (compounding error) | about_orchestration (multi-step pipeline) |