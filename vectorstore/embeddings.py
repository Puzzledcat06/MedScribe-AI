"""
Vector Store — ChromaDB embeddings for semantic patient history search
"""
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ─── Paths ────────────────────────────────────────────────────────────────────
STORE_DIR = os.path.join(os.path.dirname(__file__), "chroma_store")

# ─── Lazy singletons ──────────────────────────────────────────────────────────
_client = None
_collection = None
_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=STORE_DIR)
        _collection = _client.get_or_create_collection(
            name="medical_history",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_and_store(doc_id: str, text: str, metadata: dict):
    """
    Embed text and store in ChromaDB with metadata.

    Args:
        doc_id: Unique document identifier (consult_id).
        text: Text to embed.
        metadata: Dict of filterable metadata (patient_id, diagnosis, etc.).
    """
    embedder = _get_embedder()
    collection = _get_collection()
    embedding = embedder.encode(text).tolist()
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata],
    )


def search_history(query: str, patient_id_filter: str = None, top_k: int = 3) -> list:
    """
    Search the vector store for relevant consultations.

    Args:
        query: Natural language search query.
        patient_id_filter: Optional — restrict results to a specific patient.
        top_k: Number of results.

    Returns:
        List of dicts: {consult_id, text, metadata, distance}
    """
    embedder = _get_embedder()
    collection = _get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embedder.encode(query).tolist()

    where_clause = {"patient_id": patient_id_filter} if patient_id_filter else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        where=where_clause,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for cid, doc, meta, dist in zip(ids, docs, metas, dists):
        output.append({
            "consult_id": cid,
            "text": doc,
            "metadata": meta,
            "distance": round(dist, 4),
        })
    return output


if __name__ == "__main__":
    embed_and_store(
        doc_id="TEST001",
        text="Patient P001 has fever and headache for 3 days. Diagnosis: viral fever.",
        metadata={"patient_id": "P001", "diagnosis": "viral fever", "symptoms": "fever, headache"},
    )
    results = search_history("fever headache", patient_id_filter="P001")
    for r in results:
        print(r)
