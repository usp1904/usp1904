"""
LangSmith observability — wired BEFORE any LangChain call so every LLM/retriever/chain/LangGraph node is traced.
Graceful no-op if LANGSMITH_API_KEY not set (logs locally).
"""
import os, logging
from typing import Optional

log = logging.getLogger("cbse.observability")

def init_langsmith():
    # Set tracing env before importing langchain tracers
    if os.getenv("LANGSMITH_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "cbse-x-platform")
        os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        log.info("LangSmith tracing enabled project=%s", os.environ["LANGCHAIN_PROJECT"])
        return True
    else:
        # Local fallback: don't fail, just log. LangGraph still traces locally via memory.
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        log.info("LangSmith not configured (LANGSMITH_API_KEY missing) — using local observability")
        return False

# Auto-init on import (before any agent/llm import)
init_langsmith()

def get_client():
    try:
        from langsmith import Client
        api_key = os.getenv("LANGSMITH_API_KEY")
        if not api_key:
            return None
        return Client(api_key=api_key)
    except Exception as e:
        log.debug("LangSmith client not available: %s", e)
        return None

def upsert_eval_dataset(name: str, examples: list[dict]):
    """examples: [{'question':..., 'ground_truth':..., 'subject':...}]"""
    client = get_client()
    if not client:
        log.warning("LANGSMITH_API_KEY not set — skipping dataset %s", name)
        return None
    try:
        ds = client.read_dataset(dataset_name=name) if client.has_dataset(dataset_name=name) else client.create_dataset(dataset_name=name, description="CBSE Class X eval")
        client.create_examples(
            inputs=[{"question": e["question"], "subject": e["subject"]} for e in examples],
            outputs=[{"ground_truth": e["ground_truth"]} for e in examples],
            dataset_id=ds.id,
        )
        log.info("Upserted dataset %s %d examples", name, len(examples))
        return ds
    except Exception as e:
        log.error("Dataset upsert failed %s: %s", name, e)
        return None
