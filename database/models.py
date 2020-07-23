from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime

# if user is deleted, delete list collection as well
# if post is deleted, delete ref in list collection?


class User(db.Document):
    user_name = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)

    date_created = db.DateTimeField(default=datetime.datetime.utcnow)

    bio = db.StringField(default="")

    rank_points = db.IntField(default=0)
    list_num = db.IntField(default=0)
    following_num = db.IntField(default=0)
    followers_num = db.IntField(default=0)

    created_lists = db.ReferenceField('ListCollection')

    following = db.ListField(db.ReferenceField(
        'self', reverse_delete_rule=db.PULL))
    followers = db.ListField(db.ReferenceField(
        'self', reverse_delete_rule=db.PULL))

    def hash_pass(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


# use raw query to implement search functionality
# parent_title
# item_name
# rank
# description
# picture

class RankedList(db.Document):
    user_name = db.StringField(required=True)
    created_by = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)

    date_created = db.DateTimeField(default=datetime.datetime.utcnow)

    title = db.StringField(required=True)
    num_likes = db.IntField(required=True, default=0)
    liked_users = db.ListField(db.ReferenceField(
        'User', reverse_delete_rule=db.PULL), default=[])
    rank_items = db.ListField(db.DictField(), max_length=10, default=[])


class ListCollection(db.Document):
    user_name = db.StringField(required=True, unique=True)
    belongs_to = db.ReferenceField(
        'User', reverse_delete_rule=db.CASCADE)
    rank_lists = db.ListField(db.ReferenceField(
        'RankedList', reverse_delete_rule=db.PULL))
    liked_lists = db.ListField(db.ReferenceField(
        'RankedList', reverse_delete_rule=db.PULL))
