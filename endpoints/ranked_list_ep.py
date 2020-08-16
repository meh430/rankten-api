from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from errors import *
from utils import *
from database.json_cacher import *
import datetime


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
        return Response(RankedList.objects.get(id=id).to_json(), mimetype='application/json', status=200)

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
        RankedList.objects.get(id=id, created_by=user).update(**body)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
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
        user_lists = []
        if not refresh and JsonCache.exists(key=name, itemType=USER_LISTS, page=page, sort=sort):
            user_lists = JsonCache.get_item(key=name, itemType=USER_LISTS, page=page, sort=sort)
        else:
            bounds = validate_bounds(RankedList.objects(user_name=name).count(), page)
            if not bounds:
                raise InvalidPageError
            user_lists = ranked_list_card(RankedList.objects(user_name=name).order_by(sort_options[sort])[bounds[0]:bounds[1]])
            JsonCache.cache_item(key=name, itemType=USER_LISTS, page=page, sort=sort, item=user_lists)
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

        if not refresh and JsonCache.exists(key=user.user_name, itemType=FEED, page=page):
            feed_list = JsonCache.get_item(key=user.user_name, itemType=FEED, page=page)
        else:
            for f in user.following:
                following_made = RankedList.objects(user_name=f.user_name, date_created__gte=yesterday)
                feed_list.extend(following_made)
            feed_list = sort_list(feed_list, DATE_DESC)
            feed_list = ranked_list_card(feed_list)
            JsonCache.cache_item(key=user.user_name, item=feed_list, itemType=FEED, page=page)
        
        return feed_list, 200