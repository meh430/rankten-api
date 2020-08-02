from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from database.db import get_slice_bounds
from errors import *


def json_to_ref(json_list, list_ref, user):
    rank_list = []
    for r_item in json_list:
        rank_item = RankItem(**r_item, belongs_to=list_ref, created_by=user)
        rank_item.save()
        rank_list.append(rank_item)
    return rank_list


class RankedListApi(Resource):
    # get specified list data
    @list_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def get(self, id):
        return Response(RankedList.objects.get(id=id).to_json(), mimetype='application/json', status=200)

    # update specified list
    @jwt_required
    @list_update_error
    @schema_val_error
    @internal_server_error
    def put(self, id):
        uid = get_jwt_identity()
        body = request.get_json()
        user = User.objects.get(id=uid)
        curr_list = RankedList.objects.get(id=id, created_by=user)
        curr_list.update(**body)
        return 'Updated ranked list', 200

    # delete specified list
    @jwt_required
    @list_delete_error
    @schema_val_error
    @internal_server_error
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
        commentSection = CommentSection()
        commentSection.save()
        if 'user_name' in body:
            new_list = RankedList(**body, created_by=user,
                                  comment_section=commentSection)
        else:
            new_list = RankedList(**body, created_by=user,
                                  user_name=user.user_name, comment_section=commentSection)
        new_list.save()
        commentSection.update(belongs_to=new_list)
        if 'rank_list' in body:
            new_list.update(rank_list=json_to_ref(body, user))

        user.created_lists.update(push__rank_lists=new_list)
        user.update(inc__list_num=1)
        return {'id': new_list.id}, 200


class UserRankedListsApi(Resource):
    # returns lists created by a specific user
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def get(self, name: str, page: int, sort: int):
        user = User.objects.get(user_name=name)
        user_lists = []
        if sort == 0:
            user_lists = sorted(user.created_lists.rank_lists,
                                key=lambda k: k.num_likes, reverse=True)
        elif sort == 1:
            user_lists = sorted(user.created_lists.rank_lists,
                                key=lambda k: k.date_created, reverse=True)
        elif sort == 2:
            user_lists = sorted(user.created_lists.rank_lists,
                                key=lambda k: k.date_created, reverse=False)
        list_len = len(user_lists)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        return jsonify(user_lists[lower:upper])
