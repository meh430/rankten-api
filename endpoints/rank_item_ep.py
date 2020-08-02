# get all rank items for a post? -> post id, sort by rank
# create a rank item -> post id
# delete a rank item -> rank id
# update a rank item -> rank id
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from database.db import get_slice_bounds
from errors import *


class RankItemApi(Resource):
    @list_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def get(self, id):
        # id is list id
        return jsonify(sorted(RankedList.objects.get(
            id=id).rank_list, lambda k: k.rank)), 200

    @jwt_required
    @list_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def post(self, id):
        # id is list id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        rank_list = RankedList.objects.get(id=id, created_by=user)
        body = request.get_json()
        rank_item = RankItem(**body, belongs_to=rank_list, created_by=user)
        rank_item.save()
        rank_list.update(push__rank_list=rank_item)

        return {'_id': rank_item.id}, 200

    @jwt_required
    @rank_delete_error
    @schema_val_error
    @internal_server_error
    def delete(self, id):
        # id is rank item id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        rank_item = RankItem.objects.get(id=id, created_by=user)
        rank_item.delete()

        return 'Deleted rank item', 200

    @jwt_required
    @rank_update_error
    @schema_val_error
    @internal_server_error
    def put(self, id):
        # id is rank item id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        rank_item = RankItem.objects.get(id=id, created_by=user)
        body = request.get_json()
        rank_item.update(**body)

        return 'Updated rank item', 200
