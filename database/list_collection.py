from .db import db


class ListCollection(db.Document):
    user_name = db.StringField(required=True, unique=True)
    user_id = db.ObjectIdField(required=True, unique=True)
    public_lists = db.ListField(db.ObjectIdField(), required=True)
    private_lists = db.ListField(db.ObjectIdField(), required=True)
