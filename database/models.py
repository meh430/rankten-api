from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime


class User(db.Document):
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)

    user_name = db.StringField(required=True, unique=True, max_length=15)
    password = db.StringField(required=True, min_length=6)

    bio = db.StringField()
    prof_pic = db.StringField()
    rank_points = db.IntField(default=0)

    following_num = db.IntField(default=0)
    followers_num = db.IntField(default=0)
    following = db.ListField(db.ReferenceField(
        'self', reverse_delete_rule=db.PULL))
    followers = db.ListField(db.ReferenceField(
        'self', reverse_delete_rule=db.PULL))

    list_num = db.IntField(default=0)
    created_lists = db.ReferenceField('ListCollection')

    def hash_pass(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class RankItem(db.Document):
    belongs_to = db.ReferenceField('RankedList')
    item_name = db.StringField(required=True)
    rank = db.IntField(required=True)
    description = db.StringField()
    picture = db.StringField()


class RankedList(db.Document):
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)
    created_by = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    user_name = db.StringField(required=True)
    title = db.StringField(required=True)
    num_likes = db.IntField(required=True, default=0)
    liked_users = db.ListField(db.ReferenceField(
        'User', reverse_delete_rule=db.PULL))
    rank_list = db.ListField(db.ReferenceField(
        'RankItem', reverse_delete_rule=db.PULL), max_length=10)

    comment_section = db.ReferenceField('CommentSection')


RankedList.register_delete_rule(RankItem, 'belongs_to', db.CASCADE)


class Comment(db.Document):
    made_by = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    user_name = db.StringField(required=True)
    comment = db.StringField(required=True)
    num_likes = db.IntField(default=0)
    liked_users = db.ListField(db.ReferenceField(
        'User', reverse_delete_rule=db.PULL))


class CommentSection(db.Document):
    belongs_to = db.ReferenceField(
        'RankedList', reverse_delete_rule=db.CASCADE)
    comments = db.ListField(db.ReferenceField(
        'Comment', reverse_delete_rule=db.PULL))


class ListCollection(db.Document):
    belongs_to = db.ReferenceField(
        'User', reverse_delete_rule=db.CASCADE)
    rank_lists = db.ListField(db.ReferenceField(
        'RankedList', reverse_delete_rule=db.PULL))
    liked_lists = db.ListField(db.ReferenceField(
        'RankedList', reverse_delete_rule=db.PULL))
