"""llmSquire — Koans for mastering LLM invocation, harness creation, skills, and evaluation-driven development."""
from llmsquire.koan import Koan, _fill_, FillMeInError, _FillMeIn
from llmsquire.llm_client import LLMClient, LLMResponse, InteractionRecord, create_llm_client
from llmsquire.proxy import llm

__version__ = "0.1.0"
__all__ = [
    "Koan",
    "llm",
    "_fill_",
    "FillMeInError",
    "_FillMeIn",
    "LLMClient",
    "LLMResponse",
    "InteractionRecord",
    "create_llm_client",
]