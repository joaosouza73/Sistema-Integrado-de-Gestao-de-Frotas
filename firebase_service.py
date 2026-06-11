import os

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

_db = None
FIRESTORE_TIMEOUT = 15


def get_firestore():
    global _db

    if _db is not None:
        return _db

    credentials_path = os.getenv("FIREBASE_CREDENTIALS", "firebase-service-account.json")

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Arquivo de credenciais do Firebase não encontrado: {credentials_path}"
        )

    if not firebase_admin._apps:
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


def doc_to_dict(doc):
    data = doc.to_dict() or {}
    data["_id"] = doc.id
    return data


def list_documents(collection_name, order_by=None, descending=False, limit=None):
    query = get_firestore().collection(collection_name)

    if order_by:
        direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
        query = query.order_by(order_by, direction=direction)

    if limit:
        query = query.limit(limit)

    return [doc_to_dict(doc) for doc in query.stream(timeout=FIRESTORE_TIMEOUT)]


def find_one(collection_name, field, value):
    query = (
        get_firestore()
        .collection(collection_name)
        .where(filter=FieldFilter(field, "==", value))
        .limit(1)
        .stream(timeout=FIRESTORE_TIMEOUT)
    )

    for doc in query:
        return doc_to_dict(doc)

    return None


def create_document(collection_name, data, document_id=None):
    collection = get_firestore().collection(collection_name)
    doc_ref = collection.document(document_id) if document_id else collection.document()
    doc_ref.set(data, timeout=FIRESTORE_TIMEOUT)
    return doc_ref.id


def update_document(collection_name, document_id, data):
    get_firestore().collection(collection_name).document(document_id).update(
        data,
        timeout=FIRESTORE_TIMEOUT,
    )


def delete_document(collection_name, document_id):
    get_firestore().collection(collection_name).document(document_id).delete(
        timeout=FIRESTORE_TIMEOUT,
    )


def firebase_status():
    try:
        get_firestore()
        return True, "Firebase conectado."
    except Exception as exc:
        return False, str(exc)
