"""
MoneyMap – Firebase / Firestore Database Helper
Supports both local (JSON file) and Render (env var JSON string) credential loading.
"""
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import json
import os
from datetime import datetime

# ── Initialise Firebase Admin SDK (singleton) ──────────────────────
_app = None

def _get_app():
    global _app
    if _app is None:
        # On Render: FIREBASE_CREDENTIALS_JSON env var holds the full JSON string
        env_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
        if env_json:
            cred_dict = json.loads(env_json)
            cred = credentials.Certificate(cred_dict)
        else:
            # Local dev: read from file path in config
            from config import FIREBASE_CREDENTIALS_PATH
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        _app = firebase_admin.initialize_app(cred)
    return _app

def get_db() -> firestore.client:
    """Return the Firestore client, initialising Firebase if needed."""
    _get_app()
    return firestore.client()

# ─────────────────────────────────────────────────────────────────────
# Generic CRUD helpers
# ─────────────────────────────────────────────────────────────────────

def new_id() -> str:
    """Generate a unique document ID."""
    return str(uuid.uuid4())

def ts_now() -> str:
    """Current UTC datetime as ISO string."""
    return datetime.utcnow().isoformat()

# ── CREATE ────────────────────────────────────────────────────────────
def create_doc(collection: str, data: dict, doc_id: str = None) -> str:
    """
    Add a document to *collection*.
    If doc_id is given it is used; otherwise a new UUID is generated.
    Returns the document id.
    """
    db = get_db()
    doc_id = doc_id or new_id()
    data.setdefault("created_at", ts_now())
    db.collection(collection).document(doc_id).set(data)
    return doc_id

# ── READ ──────────────────────────────────────────────────────────────
def get_doc(collection: str, doc_id: str) -> dict | None:
    """Return a single document as dict (with 'id' key), or None."""
    db = get_db()
    snap = db.collection(collection).document(doc_id).get()
    if snap.exists:
        d = snap.to_dict()
        d["id"] = snap.id
        return d
    return None

def query_docs(collection: str, filters: list[tuple] = None,
               order_by: str = None, desc: bool = False,
               limit: int = None) -> list[dict]:
    """
    Query a collection with optional equality filters.
    filters  – list of (field, op, value) tuples, e.g. [("user_id","==","abc")]
    Returns list of dicts, each with an added "id" key.
    """
    db  = get_db()
    ref = db.collection(collection)
    if filters:
        for field, op, value in filters:
            ref = ref.where(field, op, value)
    if order_by:
        direction = firestore.Query.DESCENDING if desc else firestore.Query.ASCENDING
        ref = ref.order_by(order_by, direction=direction)
    if limit:
        ref = ref.limit(limit)
    docs = ref.stream()
    result = []
    for snap in docs:
        d = snap.to_dict()
        d["id"] = snap.id
        result.append(d)
    return result

# ── UPDATE ────────────────────────────────────────────────────────────
def update_doc(collection: str, doc_id: str, data: dict) -> None:
    """Partial update (merge) a document."""
    db = get_db()
    db.collection(collection).document(doc_id).update(data)

# ── DELETE ────────────────────────────────────────────────────────────
def delete_doc(collection: str, doc_id: str) -> None:
    """Delete a document."""
    db = get_db()
    db.collection(collection).document(doc_id).delete()

def delete_docs(collection: str, filters: list[tuple]) -> int:
    """Delete all documents matching *filters*. Returns count deleted."""
    docs  = query_docs(collection, filters=filters)
    db    = get_db()
    count = 0
    for d in docs:
        db.collection(collection).document(d["id"]).delete()
        count += 1
    return count