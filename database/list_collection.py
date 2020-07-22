from .db import db


class ListCollection(db.Document):
    user_name = db.StringField(required=True, unique=True)
    rank_lists = db.ListField(db.ObjectIdField(), default=[])
