"""
AI Medical Conversation Intelligence — Streamlit Doctor Dashboard
Run: streamlit run ui/app.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import tempfile
import json
from datetime import datetime

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedScribe AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark medical theme */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1528 50%, #0a1520 100%);
        color: #e2e8f0;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1b2d 0%, #0a1220 100%);
        border-right: 1px solid #1e3a5f;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #38bdf8;
    }

    /* ── Cards ── */
    .card {
        background: linear-gradient(135deg, #111827, #1a253a);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(56,189,248,0.12);
    }

    /* ── Section Headers ── */
    .section-title {
        color: #38bdf8;
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border-bottom: 2px solid #1e3a5f;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }

    /* ── SOAP sections ── */
    .soap-s { border-left: 4px solid #34d399; padding-left: 14px; margin-bottom: 12px; }
    .soap-o { border-left: 4px solid #60a5fa; padding-left: 14px; margin-bottom: 12px; }
    .soap-a { border-left: 4px solid #f59e0b; padding-left: 14px; margin-bottom: 12px; }
    .soap-p { border-left: 4px solid #a78bfa; padding-left: 14px; margin-bottom: 12px; }
    .soap-label {
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .soap-s .soap-label  { color: #34d399; }
    .soap-o .soap-label  { color: #60a5fa; }
    .soap-a .soap-label  { color: #f59e0b; }
    .soap-p .soap-label  { color: #a78bfa; }
    .soap-text { color: #cbd5e1; font-size: 0.93rem; line-height: 1.6; }

    /* ── Insight tags ── */
    .tag {
        display: inline-block;
        background: #1e3a5f;
        color: #93c5fd;
        border: 1px solid #2563eb40;
        border-radius: 999px;
        padding: 3px 12px;
        font-size: 0.8rem;
        margin: 3px 4px 3px 0;
        font-weight: 500;
    }
    .tag-sym  { background: #164e3420; border-color: #34d39940; color: #34d399; }
    .tag-med  { background: #31194a20; border-color: #a78bfa40; color: #a78bfa; }
    .tag-diag { background: #3730a320; border-color: #818cf840; color: #818cf8; }

    /* ── Severity badges ── */
    .sev-mild     { background:#14532d; color:#4ade80; }
    .sev-moderate { background:#78350f; color:#fcd34d; }
    .sev-severe   { background:#7f1d1d; color:#f87171; }
    .severity-badge {
        display:inline-block;
        padding: 3px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── Metric cards ── */
    div[data-testid="metric-container"] {
        background: #111827;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 12px 16px;
    }
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }

    /* ── Transcript box ── */
    .transcript-box {
        background: #0d1528;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 16px;
        font-size: 0.9rem;
        color: #94a3b8;
        line-height: 1.7;
        max-height: 200px;
        overflow-y: auto;
    }

    /* ── History card ── */
    .history-card {
        background: #0f1b2d;
        border: 1px solid #1e3a5f40;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .history-meta {
        color: #64748b;
        font-size: 0.78rem;
        margin-bottom: 8px;
    }
    .history-text {
        color: #94a3b8;
        font-size: 0.85rem;
        line-height: 1.6;
    }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(90deg, #0f2547 0%, #0c3466 50%, #0f2547 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
        border: 1px solid #1e3a5f;
        box-shadow: 0 4px 32px rgba(56,189,248,0.1);
    }
    .main-header h1 {
        color: #38bdf8;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #94a3b8;
        margin: 6px 0 0;
        font-size: 0.95rem;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        box-shadow: 0 4px 16px rgba(37,99,235,0.4);
        transform: translateY(-1px);
    }

    /* inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: #111827 !important;
        border: 1px solid #1e3a5f !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* divider */
    hr { border-color: #1e3a5f !important; }

    /* success / error */
    .stSuccess { background: #14532d !important; border: 1px solid #16a34a; border-radius: 10px; }
    .stError   { background: #7f1d1d !important; border: 1px solid #dc2626; border-radius: 10px; }

    /* scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0e1a; }
    ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }

    /* ── Dialogue bubbles ── */
    .dialogue-box {
        background: #0d1528;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 14px 16px;
        max-height: 280px;
        overflow-y: auto;
    }
    .dialogue-turn { margin-bottom: 10px; display: flex; flex-direction: column; }
    .dialogue-doctor { align-items: flex-start; }
    .dialogue-patient { align-items: flex-end; }
    .dialogue-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 3px;
    }
    .dialogue-doctor .dialogue-label { color: #38bdf8; }
    .dialogue-patient .dialogue-label { color: #34d399; }
    .dialogue-bubble {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 12px;
        font-size: 0.88rem;
        line-height: 1.55;
        max-width: 90%;
    }
    .dialogue-doctor .dialogue-bubble {
        background: #152a4a;
        color: #bfdbfe;
        border-bottom-left-radius: 3px;
    }
    .dialogue-patient .dialogue-bubble {
        background: #134034;
        color: #a7f3d0;
        border-bottom-right-radius: 3px;
    }

    /* ── Summary card ── */
    .summary-card {
        background: linear-gradient(135deg, #0f2547 0%, #0c2d52 100%);
        border: 1px solid #1e4a7a;
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
    }
    .summary-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .summary-text {
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def tags_html(items: list, cls: str) -> str:
    if not items:
        return '<span style="color:#64748b;font-size:0.85rem;">None recorded</span>'
    return "".join(f'<span class="tag {cls}">{i}</span>' for i in items)


def severity_badge(sev: str) -> str:
    cls_map = {"mild": "sev-mild", "moderate": "sev-moderate", "severe": "sev-severe"}
    cls = cls_map.get((sev or "").lower(), "sev-mild")
    return f'<span class="severity-badge {cls}">{sev or "Unknown"}</span>'


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🩺 MedScribe AI")
    st.markdown("---")

    st.markdown("#### 👤 Patient Information")
    patient_id   = st.text_input("Patient ID *", placeholder="e.g. P001", key="pid")
    patient_name = st.text_input("Patient Name", placeholder="e.g. Rajesh Kumar")
    patient_age  = st.number_input("Age", min_value=0, max_value=120, value=30, step=1)
    patient_gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])

    st.markdown("---")
    st.markdown("#### ⚙️ Pipeline Mode")
    use_mock = st.toggle("Use Mock Transcript (no audio needed)", value=True)

    st.markdown("---")
    st.markdown("#### 📖 Navigation")
    page = st.radio(
        "Go to",
        ["🏠 New Consultation", "📂 Patient History", "🔍 Semantic Search"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("AI Medical Scribe System v1.0")
    st.caption("Powered by Whisper · Groq Llama3 · ChromaDB")


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🩺 MedScribe AI</h1>
    <p>AI-powered doctor–patient conversation intelligence system</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: NEW CONSULTATION
# ═══════════════════════════════════════════════════════════════════════════════
if "🏠 New Consultation" in page:

    col_upload, col_info = st.columns([3, 2])

    with col_upload:
        st.markdown('<div class="section-title">📤 Consultation Input</div>', unsafe_allow_html=True)

        if use_mock:
            st.info("Mock mode is ON — using a pre-written transcript for demo purposes.")
            mock_text = st.text_area(
                "Mock Transcript",
                value=(
                    "Doctor: Good morning, what brings you in today?\n"
                    "Patient: I have been having high fever and severe headache for the past 3 days. "
                    "Also feeling very nauseous.\n"
                    "Doctor: Any rash, or pain behind the eyes?\n"
                    "Patient: Yes, pain behind the eyes and some body ache. Temperature was 102°F yesterday.\n"
                    "Doctor: These are classic symptoms of viral fever, possibly dengue. "
                    "I will prescribe you paracetamol 500mg twice daily and ORS for hydration. "
                    "Please get a CBC blood test done today. "
                    "Avoid self-medicating with antibiotics. "
                    "Come back in 2 days if fever doesn't reduce or if platelet count drops."
                ),
                height=200,
            )
            audio_path = None
        else:
            st.caption("Upload a WAV, MP3, or M4A audio file of the consultation.")
            uploaded_file = st.file_uploader(
                "Upload Consultation Audio",
                type=["wav", "mp3", "m4a", "ogg"],
                label_visibility="collapsed",
            )
            mock_text = None
            audio_path = None
            if uploaded_file:
                audio_dir = os.path.join(os.path.dirname(__file__), "..", "audio")
                os.makedirs(audio_dir, exist_ok=True)
                safe_name = f"{patient_id or 'unknown'}_{uploaded_file.name}"
                audio_path = os.path.join(audio_dir, safe_name)
                with open(audio_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.audio(uploaded_file)
                st.success(f"Audio saved: {safe_name}")

    with col_info:
        st.markdown('<div class="section-title">ℹ️ How It Works</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="card" style="margin-top:0">
<p style="color:#94a3b8;font-size:0.88rem;line-height:1.8;margin:0">
🎙️ <b style="color:#38bdf8">Transcription</b> — Whisper converts audio to text<br>
🔒 <b style="color:#34d399">Privacy Masking</b> — PII removed before LLM<br>
🧬 <b style="color:#a78bfa">NER</b> — SciSpacy extracts medical entities<br>
🤖 <b style="color:#f59e0b">LLM Reasoning</b> — Groq Llama3 structures insights<br>
📋 <b style="color:#60a5fa">SOAP Notes</b> — Clinical documentation auto-generated<br>
💾 <b style="color:#fb923c">Storage</b> — SQLite + ChromaDB persists all data
</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Run Pipeline Button ────────────────────────────────────────────────────
    run_ready = bool(patient_id) and (use_mock or audio_path)
    if not patient_id:
        st.warning("⚠️ Please enter a Patient ID in the sidebar to proceed.")

    if run_ready:
        if st.button("🚀 Analyze Consultation", use_container_width=True):
            from agents.pipeline import run_pipeline

            with st.spinner("Running AI pipeline... this may take 20-40 seconds on first run."):
                result = run_pipeline(
                    patient_id=patient_id,
                    audio_path=audio_path,
                    mock_transcript=mock_text if use_mock else None,
                    patient_name=patient_name or None,
                    patient_age=int(patient_age) if patient_age else None,
                    patient_gender=patient_gender,
                )

            st.session_state["last_result"] = result
            st.success(f"✅ Analysis complete! Consultation ID: **{result.get('consult_id', 'N/A')}**")

    # ── Results ────────────────────────────────────────────────────────────────
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        insights = result.get("insights", {})
        soap_sections = result.get("soap_sections", {})

        st.markdown("---")
        st.markdown("## 📊 Analysis Results")

        # Top metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Consult ID", result.get("consult_id", "N/A"))
        with m2:
            st.metric("Patient ID", result.get("patient_id", "N/A"))
        with m3:
            st.metric("Diagnosis", insights.get("diagnosis") or "Pending")
        with m4:
            st.metric("Duration", insights.get("duration") or "N/A")

        st.markdown("---")

        # ── Clinical Summary ────────────────────────────────────────────────────
        summary = result.get("consultation_summary", "")
        if summary:
            st.markdown(f"""
<div class="summary-card">
  <div class="summary-title">📝 Consultation Summary</div>
  <div class="summary-text">{summary}</div>
</div>
""", unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])

        # ── Dialogue Transcript ──────────────────────────────────────────────────
        with col_left:
            st.markdown('<div class="section-title">💬 Consultation Transcript</div>', unsafe_allow_html=True)
            dialogue_turns = result.get("dialogue_turns", [])
            masked = result.get("masked_transcript", "")
            mf = result.get("masked_fields", {})
            if mf:
                st.caption(f"🔒 PII masked: {', '.join(f'{k} ×{v}' for k,v in mf.items())}")

            if dialogue_turns:
                turns_html = ""
                for turn in dialogue_turns:
                    spk = turn.get("speaker", "Unknown")
                    txt = turn.get("text", "")
                    css_cls = "dialogue-doctor" if spk.lower() in ("doctor", "dr") else "dialogue-patient"
                    turns_html += f"""
<div class="dialogue-turn {css_cls}">
  <div class="dialogue-label">{spk}</div>
  <div class="dialogue-bubble">{txt}</div>
</div>"""
                st.markdown(f'<div class="dialogue-box">{turns_html}</div>', unsafe_allow_html=True)
            else:
                # Fallback to plain masked transcript
                st.markdown(f'<div class="transcript-box">{masked}</div>', unsafe_allow_html=True)
        # ── Medical Entities ────────────────────────────────────────────────────
        with col_right:
            st.markdown('<div class="section-title">🧬 Medical Entities (NER)</div>', unsafe_allow_html=True)
            entities = result.get("medical_entities", [])
            if entities:
                tags = "".join(f'<span class="tag">{e}</span>' for e in entities[:20])
                st.markdown(f'<div class="card" style="margin:0">{tags}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card" style="margin:0;color:#64748b">No entities detected (SciSpacy model may not be installed)</div>', unsafe_allow_html=True)

        st.markdown("---")

        col_ins, col_soap = st.columns([1, 1])

        # ── Insights Table ──────────────────────────────────────────────────────
        with col_ins:
            st.markdown('<div class="section-title">💡 Extracted Insights</div>', unsafe_allow_html=True)
            sev = insights.get("severity", "")
            st.markdown(f"""
<div class="card" style="margin:0">
  <table style="width:100%;border-collapse:collapse;">
    <tr>
      <td style="color:#64748b;padding:6px 0;font-size:0.82rem;width:38%">SYMPTOMS</td>
      <td style="padding:6px 0">{tags_html(insights.get('symptoms') or [], 'tag-sym')}</td>
    </tr>
    <tr>
      <td style="color:#64748b;padding:6px 0;font-size:0.82rem">DIAGNOSIS</td>
      <td style="padding:6px 0">{tags_html([insights.get('diagnosis')] if insights.get('diagnosis') else [], 'tag-diag')}</td>
    </tr>
    <tr>
      <td style="color:#64748b;padding:6px 0;font-size:0.82rem">MEDICATIONS</td>
      <td style="padding:6px 0">{tags_html(insights.get('medication') or [], 'tag-med')}</td>
    </tr>
    <tr>
      <td style="color:#64748b;padding:6px 0;font-size:0.82rem">SEVERITY</td>
      <td style="padding:6px 0">{severity_badge(sev)}</td>
    </tr>
    <tr>
      <td style="color:#64748b;padding:6px 0;font-size:0.82rem;vertical-align:top">ADVICE</td>
      <td style="padding:6px 0;color:#94a3b8;font-size:0.88rem;line-height:1.5">{insights.get('doctor_advice') or '—'}</td>
    </tr>
  </table>
</div>
""", unsafe_allow_html=True)

        # ── SOAP Notes ──────────────────────────────────────────────────────────
        with col_soap:
            st.markdown('<div class="section-title">📋 SOAP Clinical Note</div>', unsafe_allow_html=True)

            def soap_block(key, label, cls):
                text = soap_sections.get(key, "") or "—"
                return f'<div class="{cls}"><div class="soap-label">{label}</div><div class="soap-text">{text}</div></div>'

            soap_html = (
                soap_block("subjective", "S — Subjective", "soap-s") +
                soap_block("objective",  "O — Objective",  "soap-o") +
                soap_block("assessment", "A — Assessment",  "soap-a") +
                soap_block("plan",       "P — Plan",        "soap-p")
            )
            st.markdown(f'<div class="card" style="margin:0">{soap_html}</div>', unsafe_allow_html=True)

            # Download button
            st.download_button(
                "⬇️ Download SOAP Note",
                data=result.get("soap_raw", ""),
                file_name=f"SOAP_{patient_id}_{result.get('consult_id', 'note')}.txt",
                mime="text/plain",
                use_container_width=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PATIENT HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif "📂 Patient History" in page:

    st.markdown("## 📂 Patient Consultation History")

    if not patient_id:
        st.warning("⚠️ Enter a Patient ID in the sidebar first.")
    else:
        from database.db import get_consultations_by_patient, get_patient

        patient_info = get_patient(patient_id)
        consultations = get_consultations_by_patient(patient_id)

        if patient_info:
            p1, p2, p3 = st.columns(3)
            with p1: st.metric("Name", patient_info.get("name") or "—")
            with p2: st.metric("Age", patient_info.get("age") or "—")
            with p3: st.metric("Total Consultations", len(consultations))
        else:
            st.info(f"No patient record found for ID: {patient_id}")

        st.markdown("---")

        if not consultations:
            st.info("No consultations found for this patient. Run a new consultation first.")
        else:
            for c in consultations:
                with st.expander(f"📅 {c.get('date', 'Unknown date')}  —  Consult #{c.get('consult_id')}  |  Dx: {c.get('diagnosis') or 'N/A'}", expanded=False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        syms = c.get("symptoms") or []
                        meds = c.get("medication") or []
                        st.markdown(f"""
**Symptoms:** {', '.join(syms) if syms else 'N/A'}

**Diagnosis:** {c.get('diagnosis') or 'N/A'}

**Medications:** {', '.join(meds) if meds else 'N/A'}

**Severity:** {c.get('severity') or 'N/A'}

**Duration:** {c.get('duration') or 'N/A'}
""")
                    with col_b:
                        st.markdown("**Doctor's Advice:**")
                        st.markdown(f"<p style='color:#94a3b8;font-size:0.9rem'>{c.get('doctor_advice') or '—'}</p>", unsafe_allow_html=True)

                    if c.get("soap_notes"):
                        st.markdown("**SOAP Note:**")
                        st.markdown(f"<div class='transcript-box' style='max-height:160px'>{c.get('soap_notes')}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SEMANTIC SEARCH
# ═══════════════════════════════════════════════════════════════════════════════
elif "🔍 Semantic Search" in page:

    st.markdown("## 🔍 Semantic History Search")
    st.caption("Ask natural language questions about a patient's past consultations using vector search.")

    if not patient_id:
        st.warning("⚠️ Enter a Patient ID in the sidebar first.")
    else:
        query = st.text_input(
            "Search Query",
            placeholder="e.g. recurring fever, past antibiotics, previous diagnoses...",
        )
        top_k = st.slider("Number of results", 1, 5, 3)

        if st.button("🔍 Search", use_container_width=True) and query:
            from backend.rag_engine import retrieve_patient_history
            with st.spinner("Searching vector database..."):
                results = retrieve_patient_history(patient_id, query, top_k=top_k)

            if not results:
                st.info("No relevant history found. This patient may not have prior consultations logged, or the vector store is empty.")
            else:
                st.success(f"Found {len(results)} relevant consultation(s):")
                for i, r in enumerate(results, 1):
                    relevance = max(0, 1 - r.get("distance", 1))
                    rel_pct = round(relevance * 100)
                    meta = r.get("metadata", {})
                    st.markdown(f"""
<div class="history-card">
  <div class="history-meta">#{i} · Consult {r.get('consult_id')} · Relevance: <b style="color:#38bdf8">{rel_pct}%</b> · Dx: <b style="color:#818cf8">{meta.get('diagnosis','N/A')}</b></div>
  <div class="history-text">{r.get('text','')[:400]}...</div>
</div>
""", unsafe_allow_html=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#334155;font-size:0.78rem'>"
    "MedScribe AI · For portfolio & educational use only · Not a medical device"
    "</p>",
    unsafe_allow_html=True,
)
