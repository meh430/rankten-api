from database.db import cache
from bson import json_util
import simdjson as json
#refresh to get uncached

#mongo index + TYPE
FOLLOWING = 'following'#expire 12 hours
FOLLOWERS = 'follwers'#expire 12 hours
LIKED_USERS = 'liked_users'#expire 2 hours

#mongo index + TYPE + page
LIKED_LISTS = 'liked_lists'#expire 2 hours
FEED = 'feed'#expire 2 hours

#cache sort for pagination
#mongo index + TYPE + page + sort
USER_LISTS = 'user_lists'#expire 0.5 hour
USER_LISTSP = 'user_listsp'#expire 0.5 hour
LIST_COMMENTS = 'list_comments'#expire 2 hours
USER_COMMENTS = 'user_comments'#expire 2 hours
DISCOVER_LIST = 'discover_list'#expires 2 hour

SEARCH_LISTS = 'search_lists'
paginated = [LIKED_LISTS, USER_LISTS, USER_LISTSP,LIST_COMMENTS, USER_COMMENTS, DISCOVER_LIST, FEED]

hours_in_sec = lambda hours: int(hours * 60 * 60)

EXPIRE = hours_in_sec(1)

serializer = json_util.default

class JsonCache:

    @staticmethod
    def cache_item(key="", itemType="", page="", sort="", item="", ex=EXPIRE):
        sort = str(sort)
        page = str(page)
        print("CACHING REQUEST: " + key + itemType + page + sort)
        if itemType == LIST_COMMENTS or itemType == USER_COMMENTS:
            cache.set(key + itemType + page + sort, json.dumps([comm.to_json() for comm in item], default=serializer), ex=ex)
        else:
            cache.set(key + itemType + page + sort, json.dumps(item, default=serializer), ex=ex)

    @staticmethod
    def get_item(key="", itemType="", page="", sort=""):
        sort = str(sort)
        page = str(page)
        print("GETTING FROM CACHE")
        if itemType == LIST_COMMENTS or itemType == USER_COMMENTS:
            comm_list = json.loads(cache.get(key + itemType + page + sort))
            return [json.loads(comm) for comm in comm_list]
        else:
            return json.loads(cache.get(key + itemType + page + sort))
 

    @staticmethod
    def exists(key="", itemType="", page="", sort=""):
        page = str(page)
        sort = str(sort)
        has_key = cache.exists(key + itemType + page + sort)
        print(key + itemType + page + sort + ": " + str(has_key))
        return has_key

    @staticmethod
    def delete(key="", itemType=""):
        cache.delete(key + itemType)

    @staticmethod
    def sort_delete(key="", itemType=""):
        for key in cache.scan_iter(key+itemType+"*"):
            cache.delete(key)

    #[key="", itemType="", page="", sort=""]
    @staticmethod
    def bulk_delete(*args):
        for item in args:
            if item['itemType'] in paginated:
                JsonCache.sort_delete(key=item['key'], itemType=item['itemType'])
            else:
                JsonCache.delete(key=item['key'], itemType=item['itemType'])
    
def key_dict(key="", itemType=""):
    return {'key': key, 'itemType': itemType}