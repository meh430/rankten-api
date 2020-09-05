from .db import db
import ujson as json
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime


class User(db.Document):
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)

    user_name = db.StringField(required=True, unique=True, max_length=15)
    password = db.StringField(required=True, min_length=6, max_length=128)

    bio = db.StringField(default="")
    prof_pic = db.StringField(default="")
    rank_points = db.IntField(default=0)

    following = db.ListField(db.ReferenceField(
        'self', reverse_delete_rule=db.PULL), default=[])
    followers = db.ListField(db.ReferenceField(
        'self', reverse_delete_rule=db.PULL), default=[])

    num_comments = db.IntField(default=0)

    list_num = db.IntField(default=0)
    created_lists = db.ReferenceField('ListCollection')

    meta = {
        'indexes': [
        {'fields': ["$bio"],
         'default_language': 'english',
        }
    ]}

    def hash_pass(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def as_json(self):
        user_json = self.to_json()
        return json.loads(user_json)


class RankItem(db.Document):
    created_by = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    belongs_to = db.ReferenceField('RankedList')

    private = db.BooleanField(default=False)

    parent_title = db.StringField(default="")
    item_name = db.StringField(required=True)
    rank = db.IntField(required=True, min_value=1, max_value=10)
    description = db.StringField(default="")
    picture = db.StringField(default="")

    meta = {
        'indexes': [
        {
            'fields': ["$item_name", "$description", "$parent_title"],
            'default_language': 'english',
            'weights': {'description': 4, 'item_name': 8, 'parent_title': 10}
        }
    ]}


class RankedList(db.Document):
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)

    created_by = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    user_name = db.StringField(required=True)

    private = db.BooleanField(default=False)

    title = db.StringField(required=True)
    rank_list = db.ListField(db.ReferenceField(
        'RankItem', reverse_delete_rule=db.PULL), max_length=10)

    num_likes = db.IntField(default=0)
    liked_users = db.ListField(db.ReferenceField(
        'User', reverse_delete_rule=db.PULL), default=[])

    num_comments = db.IntField(default=0)
    comment_section = db.ReferenceField('CommentSection')

    def as_json(self):
        list_json = self.to_json()
        return json.loads(list_json)


RankedList.register_delete_rule(RankItem, 'belongs_to', db.CASCADE)


class Comment(db.Document):
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)
    belongs_to = db.ReferenceField('CommentSection')

    made_by = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    user_name = db.StringField(required=True)

    prof_pic = db.StringField(default="")
    comment = db.StringField(required=True)
    edited = db.BooleanField(default=False)

    num_likes = db.IntField(default=0)
    liked_users = db.ListField(db.ReferenceField(
        'User', reverse_delete_rule=db.PULL), default=[])


class CommentSection(db.Document):
    belongs_to = db.ReferenceField(
        'RankedList', reverse_delete_rule=db.CASCADE)
    comments = db.ListField(db.ReferenceField(
        'Comment', reverse_delete_rule=db.PULL), default=[])


CommentSection.register_delete_rule(Comment, 'belongs_to', db.CASCADE)


class ListCollection(db.Document):
    belongs_to = db.ReferenceField(
        'User', reverse_delete_rule=db.CASCADE)
    rank_lists = db.ListField(db.ReferenceField(
        'RankedList', reverse_delete_rule=db.PULL))
    liked_lists = db.ListField(db.ReferenceField(
        'RankedList', reverse_delete_rule=db.PULL))