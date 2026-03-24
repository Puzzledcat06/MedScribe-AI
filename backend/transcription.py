"""
Transcription Module — Groq Whisper API for speech-to-text
Uses Groq's hosted Whisper (whisper-large-v3) instead of local Whisper,
so no ffmpeg installation is required on Windows.
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


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file to text using Groq's hosted Whisper API.
    Supports WAV, MP3, M4A, OGG — no local ffmpeg required.

    Args:
        file_path: Absolute or relative path to the audio file.

    Returns:
        Transcribed text string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    client = _get_groq()

    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), audio_file.read()),
            model="whisper-large-v3",
            response_format="text",
            language="en",
        )

    # Groq returns a string directly when response_format="text"
    if isinstance(transcription, str):
        return transcription.strip()
    return transcription.text.strip()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = transcribe_audio(sys.argv[1])
        print("Transcript:", text)
    else:
        print("Usage: python transcription.py <audio_file>")
