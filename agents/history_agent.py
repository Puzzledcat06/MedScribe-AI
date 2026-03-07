"""
History Agent — retrieves relevant past consultations via vector search
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.rag_engine import retrieve_patient_history
from database.db import get_consultations_by_patient, get_patient


class HistoryAgent:
    """Agent that retrieves patient history from SQLite and ChromaDB."""

    def run(self, context: dict) -> dict:
        """
        Expects context keys:
          - patient_id (str)
          - history_query (str, optional): search query for vector retrieval
        Adds to context:
          - past_consultations (list): from SQLite (all previous, structured)
          - relevant_history (list): from ChromaDB (semantic search results)
          - patient_info (dict): patient record
        """
        patient_id = context.get("patient_id", "")
        query = context.get("history_query", "symptoms and diagnosis")

        context["patient_info"] = get_patient(patient_id)
        context["past_consultations"] = get_consultations_by_patient(patient_id)

        try:
            context["relevant_history"] = retrieve_patient_history(
                patient_id=patient_id,
                query=query,
                top_k=3,
            )
        except Exception as e:
            print(f"[HistoryAgent] Vector search skipped: {e}")
            context["relevant_history"] = []

        print(f"[HistoryAgent] Found {len(context['past_consultations'])} consultation(s) for {patient_id}")
        return context
