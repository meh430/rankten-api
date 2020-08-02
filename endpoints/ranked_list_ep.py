from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import RankedList, User, ListCollection, RankItem
from database.db import get_slice_bounds
# manipulate a list
from errors import check_ps


class RankedListApi(Resource):
    # get specified list data
    def get(self, id):
        return Response(RankedList.objects.get(id=id).to_json(), mimetype='application/json', status=200)

    # update specified list
    # TODO: validate sent data
    @jwt_required
    def put(self, id):
        # TODO: check if the req to update is coming from the owner of the list
        uid = get_jwt_identity()
        body = request.get_json()
        curr_list = RankedList.objects.get(id=id, created_by=uid)
        rank_items = []
        if 'rank_list' in body:
            for rlist in body['rank_list']:
                r_item = RankItem(**rlist, belongs_to=user)
                r_item.save()
                rank_items.append(r_item)

            curr_list.update(rank_list=rank_items)

        curr_list.update(**body)

        return 'Updated ranked list', 200

    # delete specified list
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

        rank_items = []
        if 'rank_list' in body:
            for rlist in body['rank_list']:
                r_item = RankItem(**rlist, belongs_to=user)
                r_item.save()
                rank_items.append(r_item)
            new_list.update(rank_list=rank_items)

        user.created_lists.update(push__rank_lists=new_list)
        user.update(inc__list_num=1)
        return {'id': str(new_list.id)}, 200


class UserRankedListsApi(Resource):
    # returns lists created by a specific user
    # TODO: implement sort options like newest, oldest or most liked

    @check_ps
    def get(self, name, page, sort):
        user = User.objects.get(user_name=name)
        user_lists = user.created_lists.rank_lists
        list_len = len(user_lists)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            return 'Invalid page', 400
        upper = list_len if upper >= list_len else upper
        return jsonify(user_lists[lower:upper])
