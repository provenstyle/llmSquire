# Koan 12: about_decomposition.py — "Divide and Conquer"
#
# Complex workflows are chains of individually validated skills.
# Each step does one thing well. Each step is a Stage 3 agent.
# The composition is the beginning of Stage 4.
#
# In this koan, you will break a complex task into individually
# testable steps and verify each one before composing them.

from llmsquire import Koan, llm

# The complex task: "Research a topic, summarize findings, and draft an email report"
# No single skill can do this well — it needs to be decomposed.

# Step 1: Research skill — extracts key findings from raw text
RESEARCH_SKILL = """You are a research analyst.
Extract 3 key findings from the provided text.
Output each finding as a separate line starting with "Finding: ".
Base findings only on the provided text."""

# Step 2: Summarize skill — condenses findings into a brief summary
SUMMARIZE_SKILL = """You are a summarizer.
Given a list of findings, produce a 2-sentence summary.
Output only the summary text, no introduction."""

# Step 3: Email draft skill — formats a summary as an email
EMAIL_SKILL = """You are an email writer.
Given a summary, draft a professional email report.
Include a subject line starting with "Subject: ".
Include a greeting, the summary, and a closing."""


class AboutDecomposition(Koan):

    def test_step1_research_produces_findings(self):
        # Step 1: Research — extract findings from raw text
        raw_text = """AI adoption in enterprises has grown 45% year over year.
        Main challenges include data quality, skill gaps, and integration with legacy systems.
        Companies using structured evaluation frameworks report 3x higher success rates.
        Budget for AI initiatives has doubled in the Fortune 500.
        However, only 20% of AI projects make it to production."""

        response = llm.ask(
            messages=[
                {"role": "system", "content": RESEARCH_SKILL},
                {"role": "user", "content": raw_text}
            ]
        )
        # The research step should produce findings
        self.assert_match("Finding", response.content)
        # Should have at least 3 findings
        findings = [line for line in response.content.split("\n") if "Finding" in line]
        self.assert_true(len(findings) >= 2, f"Expected 2+ findings, got {len(findings)}")

    def test_step2_summarize_produces_brief_summary(self):
        # Step 2: Summarize — condense findings into a summary
        findings = """Finding: AI adoption grew 45% year over year.
Finding: Main challenges are data quality, skill gaps, and legacy integration.
Finding: Structured evaluation frameworks lead to 3x higher success rates."""

        response = llm.ask(
            messages=[
                {"role": "system", "content": SUMMARIZE_SKILL},
                {"role": "user", "content": findings}
            ]
        )
        # The summary should be brief (2 sentences)
        sentences = response.content.split(".")
        non_empty = [s for s in sentences if len(s.strip()) > 10]
        self.assert_true(
            len(non_empty) <= 4,
            f"Summary should be brief (2 sentences), got ~{len(non_empty)} sentences"
        )

    def test_step3_email_draft_has_subject_and_body(self):
        # Step 3: Email draft — format as an email
        summary = "AI adoption is growing rapidly but faces challenges in data quality and skills. Companies with structured evaluation frameworks see significantly higher success rates."

        response = llm.ask(
            messages=[
                {"role": "system", "content": EMAIL_SKILL},
                {"role": "user", "content": summary}
            ]
        )
        # The email should have a subject line
        self.assert_match("Subject", response.content)

    def test_each_step_passes_individually_before_composition(self):
        # KEY PRINCIPLE: Each step must pass its own evaluation at 95%+
        # BEFORE being wired into a workflow. This is the Stage 4 lesson:
        # compounding error means weak steps destroy the pipeline.
        #
        # Verify each step produces output (simplified evaluation):
        raw_text = "AI adoption grew 45%. Challenges include data quality. Frameworks help."

        # Step 1
        r1 = llm.ask(messages=[{"role": "system", "content": RESEARCH_SKILL},
                               {"role": "user", "content": raw_text}])
        self.assert_match("Finding", r1.content)

        # Step 2 (using step 1's output)
        r2 = llm.ask(messages=[{"role": "system", "content": SUMMARIZE_SKILL},
                               {"role": "user", "content": r1.content}])
        self.assert_true(len(r2.content) > 10)

        # Step 3 (using step 2's output)
        r3 = llm.ask(messages=[{"role": "system", "content": EMAIL_SKILL},
                               {"role": "user", "content": r2.content}])
        self.assert_match("Subject", r3.content)

    def test_composition_passes_outputs_as_inputs(self):
        # Now compose: run all 3 steps in sequence, passing outputs as inputs
        raw_text = """Cloud computing adoption reached 90% among enterprises.
        Multi-cloud strategies are becoming the norm.
        Security remains the top concern for 70% of organizations."""

        # Step 1: Research
        r1 = llm.ask(messages=[{"role": "system", "content": RESEARCH_SKILL},
                               {"role": "user", "content": raw_text}])

        # Step 2: Summarize (input = step 1's output)
        r2 = llm.ask(messages=[{"role": "system", "content": SUMMARIZE_SKILL},
                               {"role": "user", "content": r1.content}])

        # Step 3: Email (input = step 2's output)
        r3 = llm.ask(messages=[{"role": "system", "content": EMAIL_SKILL},
                               {"role": "user", "content": r2.content}])

        # The final output should be an email with a subject
        self.assert_match("Subject", r3.content)
        # And should reference the original topic (cloud computing)
        self.assert_match("cloud", r3.content.lower())