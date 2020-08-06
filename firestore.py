import firebase_admin
from firebase_admin import credentials, firestore

json_path = 'game-f05a7-firebase-adminsdk-1x4g8-502fe9809b.json'
cred = credentials.Certificate(json_path)
firebase_admin.initialize_app(cred)


def colltn_list():
    colltn = ('User', 'Game')
    return colltn


def add_record(colltn, doc, dict):
    db = firestore.client()
    db.collection(colltn).document(doc).set(dict)


def update_record(colltn, doc, dict):
    db = firestore.client()
    db.collection(colltn).document(doc).set(dict, merge=True)


def get_record(colltn, doc):
    db = firestore.client()
    record = db.collection(colltn).document(doc).get()

    if record.exists:
        return record.to_dict()
    else:
        return None


def delete_doc(colltn, doc):
    db = firestore.client()
    db.collection(colltn).document(doc).delete()
