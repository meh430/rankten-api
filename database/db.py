from flask_mongoengine import MongoEngine
import redis
import os

db = MongoEngine()
cache = redis.Redis()


def init_db(app):
    db.init_app(app)