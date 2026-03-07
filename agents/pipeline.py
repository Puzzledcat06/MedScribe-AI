"""
Pipeline Orchestrator -- runs all agents in sequence
"""
import sys
import os

# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.transcription_agent import TranscriptionAgent
from agents.privacy_agent import PrivacyAgent
from agents.extraction_agent import ExtractionAgent
from agents.storage_agent import StorageAgent
from agents.history_agent import HistoryAgent


def run_pipeline(
    patient_id: str,
    audio_path: str = None,
    mock_transcript: str = None,
    patient_name: str = None,
    patient_age: int = None,
    patient_gender: str = None,
    history_query: str = "symptoms and diagnosis",
) -> dict:
    """
    Run the full medical AI pipeline.

    Args:
        patient_id: Unique patient ID.
        audio_path: Path to audio file (used if no mock_transcript).
        mock_transcript: Pre-defined text to skip Whisper.
        patient_name / patient_age / patient_gender: Optional patient details.
        history_query: Query for semantic history retrieval.

    Returns:
        Final context dict with all extracted data.
    """
    context = {
        "patient_id": patient_id,
        "audio_path": audio_path,
        "mock_transcript": mock_transcript,
        "patient_name": patient_name,
        "patient_age": patient_age,
        "patient_gender": patient_gender,
        "history_query": history_query,
    }

    agents = [
        TranscriptionAgent(),
        PrivacyAgent(),
        ExtractionAgent(),
        StorageAgent(),
        HistoryAgent(),
    ]

    print("\n" + "-"*60)
    print("  AI MEDICAL CONVERSATION INTELLIGENCE - PIPELINE")
    print("-"*60)

    for agent in agents:
        agent_name = agent.__class__.__name__
        print(f"\n>> Running {agent_name}...")
        try:
            context = agent.run(context)
        except Exception as e:
            print(f"  X {agent_name} failed: {e}")
            context[f"{agent_name}_error"] = str(e)

    print("\n" + "-"*60)
    print("  PIPELINE COMPLETE")
    print(f"  Consult ID : {context.get('consult_id', 'N/A')}")
    print(f"  Patient    : {patient_id}")
    print(f"  Diagnosis  : {context.get('insights', {}).get('diagnosis', 'N/A')}")
    print("-"*60 + "\n")

    return context


if __name__ == "__main__":
    # Demo with mock transcript
    MOCK = (
        "Doctor: Good morning, what brings you in today? "
        "Patient: I have been having high fever and severe headache for the past 3 days. "
        "Also feeling very nauseous. "
        "Doctor: Any rash, or pain behind the eyes? "
        "Patient: Yes, pain behind the eyes and some body ache. "
        "Doctor: These are classic symptoms of viral fever, possibly dengue. "
        "I will prescribe you paracetamol 500mg twice daily, ORS for hydration, "
        "and a CBC blood test. Please avoid self-medicating with antibiotics. "
        "Come back in 2 days if fever doesn't reduce."
    )

    result = run_pipeline(
        patient_id="P001",
        mock_transcript=MOCK,
        patient_name="Demo Patient",
        patient_age=32,
        patient_gender="Male",
    )

    import json
    print("INSIGHTS:")
    print(json.dumps(result.get("insights", {}), indent=2))
    print("\nSOAP NOTE:")
    print(result.get("soap_raw", ""))
