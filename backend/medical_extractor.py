"""
Medical Extractor — SciSpacy NER + Groq LLM insight extraction
"""
import os
import json
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


# ─── Groq client ──────────────────────────────────────────────────────────────
_groq_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=_get_api_key())
    return _groq_client


# ─── SciSpacy NER ─────────────────────────────────────────────────────────────
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_sci_sm")
        except Exception:
            # Fallback: spacy/model not available, return empty list
            _nlp = "unavailable"
    return _nlp


def extract_medical_entities(text: str) -> list:
    """
    Extract biomedical named entities using SciSpacy.

    Returns:
        List of unique entity strings.
    """
    nlp = _get_nlp()
    if nlp == "unavailable":
        return []
    doc = nlp(text)
    return list({ent.text.lower() for ent in doc.ents if len(ent.text) > 2})


# ─── LLM Insight Extraction ───────────────────────────────────────────────────
def extract_insights_llm(transcript: str, entities: list = None) -> dict:
    """
    Use Groq Llama3 to extract structured medical insights from the transcript.

    Returns:
        Dict with keys: symptoms, duration, diagnosis, medication, doctor_advice
    """
    entity_hint = ""
    if entities:
        entity_hint = f"\n\nDetected medical terms (use as hints): {', '.join(entities)}"

    prompt = f"""You are a clinical AI assistant. Extract structured medical insights from the following doctor-patient conversation transcript.

Transcript:
{transcript}{entity_hint}

Return ONLY a valid JSON object with exactly these keys:
{{
  "symptoms": ["list of symptoms mentioned"],
  "duration": "how long symptoms have been present",
  "diagnosis": "suspected or confirmed diagnosis",
  "medication": ["list of medications prescribed or mentioned"],
  "doctor_advice": "summary of doctor's advice or follow-up instructions",
  "severity": "mild / moderate / severe"
}}

If any field cannot be determined, use null or an empty list. Return ONLY the JSON, no extra text."""

    client = _get_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "symptoms": [],
            "duration": None,
            "diagnosis": None,
            "medication": [],
            "doctor_advice": raw,
            "severity": None,
        }



# ─── Consultation Summary ─────────────────────────────────────────────────────
def generate_summary(transcript: str, insights: dict = None) -> str:
    """
    Generate a concise 3-sentence clinical summary of the consultation.
    Preserves all key medical content (symptoms, diagnosis, plan).
    """
    context = ""
    if insights:
        context = f"""
Key findings already extracted:
- Symptoms: {', '.join(insights.get('symptoms', []) or [])}
- Diagnosis: {insights.get('diagnosis') or 'unknown'}
- Medications: {', '.join(insights.get('medication', []) or [])}
- Severity: {insights.get('severity') or 'unknown'}
- Advice: {insights.get('doctor_advice') or ''}
"""

    prompt = f"""You are a clinical documentation AI. Read the following doctor-patient consultation transcript and write a concise clinical summary in exactly 3 sentences.

Requirements:
- Sentence 1: Patient's chief complaints and duration
- Sentence 2: Key findings, examination results, or diagnosis
- Sentence 3: Treatment plan, medications prescribed, and follow-up
{context}
Transcript:
{transcript}

Return only the 3-sentence summary. No bullet points, no headers, no extra text."""

    client = _get_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


# ─── Transcript Formatter ─────────────────────────────────────────────────────
def format_as_dialogue(transcript: str) -> list:
    """
    Format a raw Whisper transcript into a list of dialogue turns.
    Uses Groq LLM to intelligently split and label Doctor/Patient turns.

    Returns:
        List of dicts: [{"speaker": "Doctor" | "Patient", "text": "..."}]
    """
    prompt = f"""You are a medical transcription editor. The following is a raw speech-to-text transcript of a doctor-patient consultation. Split it into individual speaking turns and label each with the speaker (Doctor or Patient).

Raw transcript:
{transcript}

Return ONLY a valid JSON array like this:
[
  {{"speaker": "Doctor", "text": "Good morning, how are you feeling?"}},
  {{"speaker": "Patient", "text": "I have chest pain for 2 weeks."}}
]

Rules:
- If unsure who is speaking, use context clues (doctors ask questions, give diagnoses; patients describe symptoms)
- Keep each turn as one natural speech segment
- Return ONLY the JSON array, no extra text."""

    client = _get_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        import json
        return json.loads(raw)
    except Exception:
        # Fallback: return as single block
        return [{"speaker": "Transcript", "text": transcript}]


if __name__ == "__main__":
    sample = (
        "Doctor: What brings you in today? "
        "Patient: I've had a high fever and severe headache for 3 days. "
        "Doctor: Any vomiting or rash? "
        "Patient: Some nausea but no rash. "
        "Doctor: Likely viral fever. I'll prescribe paracetamol 500mg twice daily and ask you to rest."
    )
    entities = extract_medical_entities(sample)
    print("Entities:", entities)
    insights = extract_insights_llm(sample, entities)
    print("Insights:", json.dumps(insights, indent=2))
