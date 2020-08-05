from flask_mongoengine import MongoEngine
import redis

db = MongoEngine()
cache = redis.Redis()


def init_db(app):
    db.init_app(app)


def get_slice_bounds(page, num_items=50):
    upper = int(page) * num_items
    lower = upper - num_items
    return (lower, upper)
