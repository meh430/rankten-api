from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)


def get_slice_bounds(page):
    upper = page * 25
    lower = upper - 25
    return (lower, upper)
