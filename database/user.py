from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime


class User(db.Document):
    user_name = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    date_created = db.DateTimeField(default=datetime.datetime.utcnow)
    bio = db.StringField(default="")
    rank_points = db.IntField(default=0)
    list_num = db.IntField(default=0)
    created_lists = db.ObjectIdField(required=True)
    liked_lists = db.ListField(db.ObjectIdField(), default=[])
    following = db.ListField(db.ObjectIdField(), default=[])
    followers = db.ListField(db.ObjectIdField(), default=[])
    following_num = db.IntField(default=0)
    followers_num = db.IntField(default=0)

    def hash_pass(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)
