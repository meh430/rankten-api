from flask_mongoengine import MongoEngine
import redis

db = MongoEngine()
cache = redis.Redis()


def init_db(app):
    db.init_app(app)