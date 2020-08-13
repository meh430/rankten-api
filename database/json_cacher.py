from database.db import cache
import simdjson as json
# mongo index + KEY
FOLLOWING = 'following'
FOLLOWERS = 'follwers'
LIST_COMMENTS = 'list_comments'
USER_COMMENTS = 'user_comments'
LIKED_USERS = 'liked_users'

EXPIRE = 60*60


class JsonCache:
    @staticmethod
    def cache_item(key, item, itemType=None):
        if itemType == LIST_COMMENTS or itemType == USER_COMMENTS:
            cache.set(key + itemType,
                      json.dumps([comm.to_json() for comm in item]), ex=EXPIRE)
        elif not itemType:
            cache.set(key + itemType, json.dumps(item), ex=EXPIRE)
        else:
            cache.set(key, json.dumps(item), ex=EXPIRE)

    @staticmethod
    def get_item(key, itemType=None):
        if itemType == LIST_COMMENTS or itemType == USER_COMMENTS:
            comm_list = json.loads(cache.get(key + itemType))
            return [json.loads(comm) for comm in comm_list]
        elif not itemType:
            return json.loads(cache.get(key + itemType))
        else:
            return json.loads(cache.get(key))

    @staticmethod
    def exists(key, itemType=None):
        return cache.exists((key+itemType) if itemType else key)

    @staticmethod
    def delete(key, itemType=None):
        cache.delete((key+itemType) if itemType else key)
