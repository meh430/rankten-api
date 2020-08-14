from database.db import cache
from bson import json_util
import simdjson as json
#refresh to get uncached

# mongo index + TYPE
FOLLOWING = 'following'#expire 12 hours
FOLLOWERS = 'follwers'#expire 12 hours
LIKED_USERS = 'liked_users'#expire 2 hours
LIKED_LISTS = 'liked_lists'#expire 2 hours
FEED = 'feed'#expire 2 hours

#cache sort for pagination
#mongo index + sort + TYPE
SEARCH_USERS = 'search_users'#expire 1 hour
SEARCH_LISTS = 'search_lists'#expire 1 hour
USER_LISTS = 'user_lists'#expire 1 hour
LIST_COMMENTS = 'list_comments'#expire 2 hours
USER_COMMENTS = 'user_comments'#expire 2 hours

hours_in_sec = lambda hours: hours * 60 * 60

EXPIRE = hours_in_sec(2)

serializer = json_util.default

class JsonCache:
    @staticmethod
    def cache_item(key, item, itemType, sort="", ex=EXPIRE):
        sort = str(sort)
        if itemType == LIST_COMMENTS or itemType == USER_COMMENTS:
            cache.set(key + sort + itemType,
                json.dumps([comm.to_json() for comm in item], default=serializer), ex=ex)
        elif itemType == SEARCH_USERS:
            pass
        else:
            cache.set(key + sort + itemType, json.dumps(item, default=serializer), ex=ex)

    @staticmethod
    def get_item(key, itemType, sort=""):
        sort = str(sort)
        if itemType == LIST_COMMENTS or itemType == USER_COMMENTS:
            comm_list = json.loads(cache.get(key + sort + itemType))
            return [json.loads(comm) for comm in comm_list]
        elif itemType == SEARCH_USERS:
            pass
        else:
            return json.loads(cache.get(key + sort + itemType))
 

    @staticmethod
    def exists(key, itemType, sort=""):
        return cache.exists(key+str(sort)+itemType)

    @staticmethod
    def delete(key, itemType):
        cache.delete(key+itemType)

    @staticmethod
    def sort_delete(key, itemType)
        for i in range(0, 3):
            cache.delete(key + i + itemType)
