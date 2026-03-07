"""
Transcription Agent — converts audio file to raw transcript
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.transcription import transcribe_audio


class TranscriptionAgent:
    """Agent responsible for converting audio to transcript."""

    def run(self, context: dict) -> dict:
        """
        Expects context keys:
          - audio_path (str): Path to the audio file OR
          - mock_transcript (str): Pre-defined text (skips Whisper)
        Adds to context:
          - transcript (str)
        """
        if context.get("mock_transcript"):
            context["transcript"] = context["mock_transcript"]
            context["transcription_source"] = "mock"
        else:
            audio_path = context.get("audio_path")
            if not audio_path:
                raise ValueError("No audio_path or mock_transcript provided.")
            context["transcript"] = transcribe_audio(audio_path)
            context["transcription_source"] = "whisper"

        print(f"[TranscriptionAgent] Transcript generated ({len(context['transcript'])} chars)")
        return context
