"""
Storage Agent — persists consultation to SQLite and ChromaDB
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.db import upsert_patient, save_consultation
from backend.rag_engine import store_consultation_embedding


class StorageAgent:
    """Agent that saves structured data to SQLite and vector DB."""

    def run(self, context: dict) -> dict:
        """
        Expects context keys:
          - patient_id (str)
          - patient_name (str, optional)
          - patient_age (int, optional)
          - patient_gender (str, optional)
          - transcript (str)
          - masked_transcript (str)
          - insights (dict)
          - soap_raw (str)
        Adds to context:
          - consult_id (str)
        """
        patient_id = context.get("patient_id", "UNKNOWN")

        # Upsert patient
        upsert_patient(
            patient_id=patient_id,
            name=context.get("patient_name"),
            age=context.get("patient_age"),
            gender=context.get("patient_gender"),
        )

        # Save consultation to SQLite
        consult_id = save_consultation(
            patient_id=patient_id,
            transcript=context.get("transcript", ""),
            masked_transcript=context.get("masked_transcript", ""),
            insights=context.get("insights", {}),
            soap_notes=context.get("soap_raw", ""),
        )
        context["consult_id"] = consult_id
        print(f"[StorageAgent] Saved consultation {consult_id} for patient {patient_id}")

        # Store embedding for RAG
        try:
            store_consultation_embedding(
                patient_id=patient_id,
                consult_id=consult_id,
                transcript=context.get("masked_transcript", ""),
                insights=context.get("insights", {}),
                soap=context.get("soap_raw", ""),
            )
            print(f"[StorageAgent] Embedding stored in ChromaDB")
        except Exception as e:
            print(f"[StorageAgent] Warning: Could not store embedding: {e}")

        return context
