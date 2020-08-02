from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import RankedList, User, ListCollection, RankItem
from database.db import get_slice_bounds
from errors import *


def json_to_ref(body, user):
    rank_items = []
    for rlist in body['rank_list']:
        r_item = RankItem(**rlist, belongs_to=user)
        r_item.save()
        rank_items.append(r_item)

    return rank_items


class RankedListApi(Resource):
    # get specified list data
    @list_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def get(self, id):
        return Response(RankedList.objects.get(id=id).to_json(), mimetype='application/json', status=200)

    # update specified list
    # TODO: validate sent data
    @list_update_error
    @schema_val_error
    @internal_server_error
    @jwt_required
    def put(self, id):
        uid = get_jwt_identity()
        body = request.get_json()
        user = User.objects.get(id=uid)
        curr_list = RankedList.objects.get(id=id, created_by=user)
        if 'rank_list' in body:
            curr_list.update(rank_list=json_to_ref(body, user))

        curr_list.update(**body)

        return 'Updated ranked list', 200

    # delete specified list
    @list_delete_error
    @schema_val_error
    @internal_server_error
    @jwt_required
    def delete(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        ranked_list = RankedList.objects.get(id=id, created_by=user)
        ranked_list.delete()
        user.update(dec__list_num=1)
        return 'Deleted ranked list', 200


class RankedListsApi(Resource):
    # create new list
    @jwt_required
    @schema_val_error
    @internal_server_error
    def post(self):
        # create post, add user to post, add post to list collection of user
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        new_list = None
        if 'user_name' in body:
            new_list = RankedList(**body, created_by=user)
        else:
            new_list = RankedList(**body, created_by=user,
                                  user_name=user.user_name)
        new_list.save()

        if 'rank_list' in body:
            new_list.update(rank_list=json_to_ref(body, user))

        user.created_lists.update(push__rank_lists=new_list)
        user.update(inc__list_num=1)
        return {'id': str(new_list.id)}, 200


class UserRankedListsApi(Resource):
    # returns lists created by a specific user
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def get(self, name, page):
        user = User.objects.get(user_name=name)
        user_lists = user.created_lists.rank_lists
        list_len = len(user_lists)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        return jsonify(user_lists[lower:upper])
