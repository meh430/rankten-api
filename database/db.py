from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)

# 1: 0 upto 25
# 2: 25 upto 50
# 3: 50 upto 75


def get_slice_bounds(page, num_items=50):
    upper = int(page) * num_items
    lower = upper - num_items
    return (lower, upper)
