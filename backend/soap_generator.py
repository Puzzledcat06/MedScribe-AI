"""
SOAP Note Generator — generates clinical SOAP notes via Groq LLM
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _get_api_key():
    """Get GROQ_API_KEY from st.secrets (Streamlit Cloud) or os.getenv (local)."""
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.getenv("GROQ_API_KEY")


_groq_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=_get_api_key())
    return _groq_client


def generate_soap(transcript: str, insights: dict = None) -> str:
    """
    Generate a SOAP clinical note from the doctor-patient transcript.

    Args:
        transcript: Masked conversation transcript.
        insights: Optional pre-extracted insights dict for additional context.

    Returns:
        Formatted SOAP note string.
    """
    context = ""
    if insights:
        context = f"""
Pre-extracted insights:
- Symptoms: {', '.join(insights.get('symptoms', []) or [])}
- Duration: {insights.get('duration', 'Unknown')}
- Diagnosis: {insights.get('diagnosis', 'Unknown')}
- Medications: {', '.join(insights.get('medication', []) or [])}
- Advice: {insights.get('doctor_advice', '')}
"""

    prompt = f"""You are a clinical documentation AI. Convert the following doctor-patient conversation into a structured SOAP clinical note.
{context}
Transcript:
{transcript}

Generate a SOAP note with exactly these four sections. Be concise and clinical:

**Subjective (S):**
[Patient-reported symptoms, complaints, history in their own words]

**Objective (O):**
[Observable findings, vital signs, physical exam notes if mentioned]

**Assessment (A):**
[Clinical diagnosis or differential diagnosis]

**Plan (P):**
[Treatment plan, medications, follow-up instructions]

Return only the SOAP note, no extra commentary."""

    client = _get_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


def parse_soap_sections(soap_text: str) -> dict:
    """
    Parse raw SOAP text into a dict with keys: subjective, objective, assessment, plan.
    """
    import re
    sections = {}
    patterns = {
        "subjective": r"\*\*Subjective.*?\*\*:?\s*(.*?)(?=\*\*Objective|\Z)",
        "objective": r"\*\*Objective.*?\*\*:?\s*(.*?)(?=\*\*Assessment|\Z)",
        "assessment": r"\*\*Assessment.*?\*\*:?\s*(.*?)(?=\*\*Plan|\Z)",
        "plan": r"\*\*Plan.*?\*\*:?\s*(.*?)(?=\Z)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, soap_text, re.DOTALL | re.IGNORECASE)
        sections[key] = match.group(1).strip() if match else ""
    return sections


if __name__ == "__main__":
    sample = (
        "Doctor: What brings you in today? "
        "Patient: I've had a high fever and severe headache for 3 days. "
        "Doctor: Any vomiting? Patient: Some nausea. "
        "Doctor: Likely viral fever. Paracetamol 500mg twice daily. Rest for 3 days."
    )
    note = generate_soap(sample)
    print(note)
    print("\nParsed:")
    import json
    print(json.dumps(parse_soap_sections(note), indent=2))
