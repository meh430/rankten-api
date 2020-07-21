from .db import db
import datetime
# use raw query to implement search functionality
# parent_title
# item_name
# rank
# description
# picture


class RankedList(db.Document):
    user_name = db.StringField(required=True, unique=True)
    user_id = db.ObjectIdField(required=True, unique=True)
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)
    title = db.StringField(required=True)
    num_likes = db.IntField(required=True)
    liked_users = db.ListField(db.ObjectIdField(), required=True)
    rank_item = db.ListField(db.DictField(), max_length=10)
