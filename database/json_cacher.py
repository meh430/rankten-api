from database.db import cache
import simdjson as json
# mongo index + KEY
FOLLOWING = 'following'
FOLLOWERS = 'follwers'
LIST_COMMENTS = 'list_comments'
USER_COMMENTS = 'user_comments'
LIKED_USERS = 'liked_users'


class JsonCache:
    @staticmethod
    def cache_item(key, item):
        cache.set(key, json.dumps(item), ex=(60*60))

    @staticmethod
    def get_item(key):
        return json.loads(cache.get(key))

    @staticmethod
    def exists(key):
        return cache.exists(key)

    @staticmethod
    def delete(key):
        cache.delete(key)
