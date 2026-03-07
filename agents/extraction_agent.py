"""
Extraction Agent — runs SciSpacy NER + Groq LLM + SOAP generator + summary + dialogue formatter
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.medical_extractor import (
    extract_medical_entities,
    extract_insights_llm,
    generate_summary,
    format_as_dialogue,
)
from backend.soap_generator import generate_soap, parse_soap_sections


class ExtractionAgent:
    """Agent that extracts medical insights, generates SOAP notes, summary, and dialogue."""

    def run(self, context: dict) -> dict:
        """
        Expects context keys:
          - masked_transcript (str)
        Adds to context:
          - medical_entities (list)
          - insights (dict)
          - soap_raw (str)
          - soap_sections (dict)
          - consultation_summary (str)
          - dialogue_turns (list of {speaker, text})
        """
        masked = context.get("masked_transcript", "")

        # Step 1: NER
        entities = extract_medical_entities(masked)
        context["medical_entities"] = entities
        print(f"[ExtractionAgent] Found {len(entities)} medical entities: {entities[:5]}")

        # Step 2: LLM insight extraction
        insights = extract_insights_llm(masked, entities)
        context["insights"] = insights
        print(f"[ExtractionAgent] Insights → Diagnosis: {insights.get('diagnosis')}")

        # Step 3: SOAP note generation
        soap_raw = generate_soap(masked, insights)
        context["soap_raw"] = soap_raw
        context["soap_sections"] = parse_soap_sections(soap_raw)
        print("[ExtractionAgent] SOAP note generated")

        # Step 4: Consultation summary
        try:
            summary = generate_summary(masked, insights)
            context["consultation_summary"] = summary
            print("[ExtractionAgent] Summary generated")
        except Exception as e:
            context["consultation_summary"] = ""
            print(f"[ExtractionAgent] Summary failed: {e}")

        # Step 5: Format as dialogue
        try:
            dialogue = format_as_dialogue(masked)
            context["dialogue_turns"] = dialogue
            print(f"[ExtractionAgent] Dialogue formatted: {len(dialogue)} turns")
        except Exception as e:
            context["dialogue_turns"] = []
            print(f"[ExtractionAgent] Dialogue format failed: {e}")

        return context
