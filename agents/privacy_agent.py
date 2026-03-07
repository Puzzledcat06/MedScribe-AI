"""
Privacy Agent — masks PII from the transcript before LLM processing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.privacy import mask_sensitive_data, get_masked_fields


class PrivacyAgent:
    """Agent that removes PII from the conversation transcript."""

    def run(self, context: dict) -> dict:
        """
        Expects context keys:
          - transcript (str)
        Adds to context:
          - masked_transcript (str)
          - masked_fields (dict): summary of what was masked
        """
        transcript = context.get("transcript", "")
        masked = mask_sensitive_data(transcript)
        context["masked_transcript"] = masked
        context["masked_fields"] = get_masked_fields(transcript, masked)
        n_masked = sum(context["masked_fields"].values())
        print(f"[PrivacyAgent] Masked {n_masked} PII instance(s): {context['masked_fields']}")
        return context
