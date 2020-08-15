# get all rank items for a post? -> post id, sort by rank
# create a rank item -> post id
# delete a rank item -> rank id
# update a rank item -> rank id
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from errors import *
from utils import *
from endpoints.ranked_list_ep import json_to_ref
from database.json_cacher import *

# /rankitem/<id>
# supports GET(list id), POST(list id), DELETE(item id), PUT(item id)
class RankItemApi(Resource):
    # return all rank items in a list
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id):
        # id is list id
        return jsonify(sorted(RankedList.objects.get(id=id).rank_list, key=lambda k: k.rank))

    # create new rank item
    # TODO: data validation?
    """
    schema:
    {
        "item_name": string,
        "rank": int between 1-10,
        "description": optional string,
        "picture": optional string
    }
    """
    @jwt_required
    @list_does_not_exist_error
    @schema_val_error
    def post(self, id):
        # id is list id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        rank_list = RankedList.objects.get(id=id, created_by=user)
        body = request.get_json()
        rank_item = RankItem(**body, belongs_to=rank_list, created_by=user)
        rank_item.save()
        rank_list.update(push__rank_list=rank_item)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
        return {'_id': str(rank_item.id)}, 200

    # delete a rank item
    @jwt_required
    @rank_delete_error
    @schema_val_error
    def delete(self, id):
        # id is rank item id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        rank_item = RankItem.objects.get(id=id, created_by=user)
        rank_item.delete()
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
        return 'Deleted rank item', 200

    # update a rank item
    """
    schema:
    {
        "item_name": string,
        "rank": int between 1-10,
        "description": optional string,
        "picture": optional string
    }
    """
    @jwt_required
    @rank_update_error
    @schema_val_error
    def put(self, id):
        # id is rank item id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        rank_item = RankItem.objects.get(id=id, created_by=user)
        body = request.get_json()
        rank_item.update(**body)
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
        return 'Updated rank item', 200

# /rankitems/<id>
# supports PUT(list id)
class BulkUpdateApi(Resource):
    # add multpile rank items to a list
    """
    schema:
    {
        "rank_list": [
            {
                "item_name": string,
                "rank": int between 1-10,
                "description": optional string,
                "picture": optional string
            }
        ]
    }
    """
    @jwt_required
    @rank_update_error
    @schema_val_error
    def put(self, id):
        # id here is list id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        rank_list = RankedList.objects.get(id=id, created_by=user)
        rank_list.update(push_all__rank_list=json_to_ref(
            body['rank_list'], rank_list, user))
        JsonCache.sort_delete(key=user.user_name, itemType=USER_LISTS)
        return 'Added rank items', 200
