"""
Database Module — SQLite schema and CRUD for patients and consultations
"""
import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "medical.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id   TEXT PRIMARY KEY,
            name         TEXT,
            age          INTEGER,
            gender       TEXT,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            consult_id          TEXT PRIMARY KEY,
            patient_id          TEXT NOT NULL,
            transcript          TEXT,
            masked_transcript   TEXT,
            symptoms            TEXT,
            duration            TEXT,
            diagnosis           TEXT,
            medication          TEXT,
            doctor_advice       TEXT,
            severity            TEXT,
            soap_notes          TEXT,
            date                TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    conn.commit()
    conn.close()
    print("DB ready:", DB_PATH)


def upsert_patient(patient_id: str, name: str = None, age: int = None, gender: str = None):
    """Insert or update a patient record."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO patients (patient_id, name, age, gender)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(patient_id) DO UPDATE SET
            name   = COALESCE(excluded.name, patients.name),
            age    = COALESCE(excluded.age, patients.age),
            gender = COALESCE(excluded.gender, patients.gender)
    """, (patient_id, name, age, gender))
    conn.commit()
    conn.close()


def save_consultation(patient_id: str, transcript: str, masked_transcript: str,
                       insights: dict, soap_notes: str) -> str:
    """Save a consultation record and return its consult_id."""
    import json
    consult_id = str(uuid.uuid4())[:8].upper()
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO consultations
        (consult_id, patient_id, transcript, masked_transcript,
         symptoms, duration, diagnosis, medication, doctor_advice,
         severity, soap_notes, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        consult_id,
        patient_id,
        transcript,
        masked_transcript,
        json.dumps(insights.get("symptoms", [])),
        insights.get("duration", ""),
        insights.get("diagnosis", ""),
        json.dumps(insights.get("medication", [])),
        insights.get("doctor_advice", ""),
        insights.get("severity", ""),
        soap_notes,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    conn.close()
    return consult_id


def get_patient(patient_id: str) -> dict:
    """Fetch a patient record by ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_consultations_by_patient(patient_id: str) -> list:
    """Fetch all consultations for a patient, newest first."""
    import json
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM consultations
        WHERE patient_id = ?
        ORDER BY date DESC
    """, (patient_id,))
    rows = c.fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        try:
            d["symptoms"] = json.loads(d.get("symptoms") or "[]")
        except Exception:
            d["symptoms"] = []
        try:
            d["medication"] = json.loads(d.get("medication") or "[]")
        except Exception:
            d["medication"] = []
        results.append(d)
    return results


# Initialize on import
init_db()

if __name__ == "__main__":
    print("DB initialized at:", DB_PATH)
    upsert_patient("P001", "Test Patient", 35, "Male")
    print("Inserted test patient P001")
