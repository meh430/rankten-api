from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from errors import *
from utils import *
from database.json_cacher import *
import datetime
import simdjson as json


def json_to_ref(json_list, list_ref, user):
    # convert list of dicts to rankitem refs for bulk updates
    rank_list = []
    for r_item in json_list:
        rank_item = RankItem(**r_item, belongs_to=list_ref, created_by=user)
        rank_item.save()
        rank_list.append(rank_item)
    return rank_list

# /rankedlist/<id>
# supports GET, PUT, DELETE
class RankedListApi(Resource):
    # get specified list data
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id):
        list_json = RankedList.objects.get(id=id).as_json()
        rank_items = sorted(RankedList.objects.get(id=id).rank_list, key=lambda k: k.rank)
        rank_items = [json.loads(r.to_json()) for r in rank_items]
        list_json['rank_list'] = rank_items
        return list_json, 200

    # update specified list
    """
    schema:
    {
        "title": string
    }
    """
    @jwt_required
    @list_update_error
    @schema_val_error
    def put(self, id):
        uid = get_jwt_identity()
        body = request.get_json()
        user = User.objects.get(id=uid)
        ranked_list = RankedList.objects.get(id=id, created_by=user)
        ranked_items = body.pop('rank_list', None)
        if ranked_items:
            #delete item if not in incoming list
            present_item_ids = [str(r.id) for r in ranked_list.rank_list]
            given_item_ids = [str(r['_id'] if '_id' in r else '2468') for r in ranked_items]
            for id in present_item_ids:
                if id not in given_item_ids:
                    RankItem.objects.get(id=id).delete()

            for ranked_item in ranked_items:
                item_id = ranked_item.pop('_id', None)
                if item_id:
                    RankItem.objects.get(id=item_id).update(**ranked_item)
                else: 
                    r_item = RankItem(**ranked_item, belongs_to=ranked_list, created_by=user)
                    r_item.save()
                    ranked_list.rank_list.append(r_item)
        
        ranked_list.rank_list = sorted(ranked_list.rank_list, key=lambda k: k.rank)
        ranked_list.save()
        ranked_list.update(**body)

        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTSP)
        return {'message': 'Updated ranked list'}, 200

    # delete specified list
    @jwt_required
    @list_delete_error
    @schema_val_error
    def delete(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        ranked_list = RankedList.objects.get(id=id, created_by=user)
        ranked_list.delete()
        user.update(dec__list_num=1)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTSP)
        return {'message': 'Deleted ranked list'}, 200

# /rankedlist
# supports POST
class RankedListsApi(Resource):
    # creates new list
    """
    schema:
    {
        "title": string,
        "rank_list": [
            {
                "item_name": string,
                "rank": int,
                "description": optional string,
                "picture": optional string
            }
        ]
    }
    """
    @jwt_required
    @schema_val_error
    def post(self):
        # create post, add user to post, add post to list collection of user
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        new_list = None
        commentSection = CommentSection()
        commentSection.save()
        rank_list = body.pop('rank_list', None)
        body.pop('num_likes', None)
        body.pop('num_comments', None)
        
        new_list = RankedList(**body, created_by=user,
                                  user_name=user.user_name, comment_section=commentSection)
        new_list.save()
        commentSection.update(belongs_to=new_list)
        if rank_list:
            new_list.update(rank_list=json_to_ref(rank_list, new_list, user))

        user.created_lists.update(push__rank_lists=new_list)
        user.update(inc__list_num=1)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTSP)
        return {'message': 'Created ranked list', '_id': str(new_list.id)}, 200

# /rankedlists/<name>/<page>/<sort>
# supports GET
class UserRankedListsApi(Resource):
    # returns lists created by a specific user
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str, page: int, sort: int):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])
            print(refresh)

        user_lists = []
        if not refresh and JsonCache.exists(key=name, itemType=USER_LISTS, page=page, sort=sort):
            user_lists = JsonCache.get_item(key=name, itemType=USER_LISTS, page=page, sort=sort)
        else:
            bounds = validate_bounds(RankedList.objects(user_name=name, private=False).count(), page)
            if not bounds:
                raise InvalidPageError
            user_lists = ranked_list_card(RankedList.objects(user_name=name, private=False).order_by(sort_options[sort])[bounds[0]:bounds[1]])
            JsonCache.cache_item(key=name, itemType=USER_LISTS, page=page, sort=sort, item=user_lists, ex=hours_in_sec(0.5))
        return user_lists, 200

# /rankedlistsp/<page>/<sort>
# supports GET
class UserRankedListsPApi(Resource):
    # returns lists created by a specific user including private ones
    @jwt_required
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    def get(self, page: int, sort: int):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        uid = get_jwt_identity()
        user = User.objects.get(id=uid)

        user_lists = []
        if not refresh and JsonCache.exists(key=user.user_name, itemType=USER_LISTSP, page=page, sort=sort):
            user_lists = JsonCache.get_item(key=user.user_name, itemType=USER_LISTSP, page=page, sort=sort)
        else:
            bounds = validate_bounds(RankedList.objects(user_name=user.user_name).count(), page)
            if not bounds:
                raise InvalidPageError
            user_lists = ranked_list_card(RankedList.objects(user_name=user.user_name).order_by(sort_options[sort])[bounds[0]:bounds[1]])
            JsonCache.cache_item(key=user.user_name, itemType=USER_LISTSP, page=page, sort=sort, item=user_lists, ex=hours_in_sec(0.5))
        return user_lists, 200

#/feed
#supports GET
class FeedApi(Resource):
    #return user feed
    @jwt_required
    @schema_val_error
    def get(self, page: int):
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(hours=24)

        page = int(page)
        if page <= 0:
            raise InvalidPageError
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        feed_list = []

        if not refresh and JsonCache.exists(key=user.user_name, itemType=FEED):
            feed_list = JsonCache.get_item(key=user.user_name, itemType=FEED)
        else:
            for f in user.following:
                following_made = RankedList.objects(user_name=f.user_name, date_created__gte=yesterday)
                feed_list.extend(following_made)
            feed_list = sort_list(feed_list, DATE_DESC)
            feed_list = ranked_list_card(feed_list)
            JsonCache.cache_item(key=user.user_name, item=feed_list, itemType=FEED)
        
        return feed_list, 200

class PrivateListApi(Resource):

    @jwt_required
    @list_does_not_exist_error
    def get(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        ranked_list = RankedList.objects.get(id=id, created_by=user)

        return ranked_list.private, 200