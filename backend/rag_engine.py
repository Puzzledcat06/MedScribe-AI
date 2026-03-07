"""
RAG Engine — ChromaDB-based patient history retrieval
"""
import os
from vectorstore.embeddings import embed_and_store, search_history


def store_consultation_embedding(patient_id: str, consult_id: str, transcript: str,
                                  insights: dict, soap: str):
    """
    Embed and store a consultation into the vector store.
    """
    # Build a rich text blob for embedding
    symptom_str = ", ".join(insights.get("symptoms", []) or [])
    med_str = ", ".join(insights.get("medication", []) or [])
    text = (
        f"Patient {patient_id} consultation {consult_id}. "
        f"Symptoms: {symptom_str}. "
        f"Diagnosis: {insights.get('diagnosis', '')}. "
        f"Medications: {med_str}. "
        f"Doctor advice: {insights.get('doctor_advice', '')}. "
        f"Transcript excerpt: {transcript[:300]}"
    )
    metadata = {
        "patient_id": patient_id,
        "consult_id": consult_id,
        "diagnosis": insights.get("diagnosis", "") or "",
        "symptoms": symptom_str,
        "medication": med_str,
    }
    embed_and_store(doc_id=consult_id, text=text, metadata=metadata)


def retrieve_patient_history(patient_id: str, query: str, top_k: int = 3) -> list:
    """
    Retrieve the most relevant past consultation summaries for a patient.

    Args:
        patient_id: Unique patient identifier.
        query: Natural language query (e.g., "recurring symptoms" or "past medications").
        top_k: Number of results to return.

    Returns:
        List of dicts with keys: consult_id, text, metadata, distance
    """
    results = search_history(
        query=f"Patient {patient_id}: {query}",
        patient_id_filter=patient_id,
        top_k=top_k,
    )
    return results
