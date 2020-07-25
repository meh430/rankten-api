from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import RankedList, User, ListCollection
from database.db import get_slice_bounds
# manipulate a list


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
        RankedList.objects.get(id=id, created_by=uid).update(**body)
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
        user.created_lists.update(push__rank_lists=new_list)
        user.created_lists.save()
        user.update(inc__list_num=1)
        return {'id': str(new_list.id)}, 200


class UserRankedListsApi(Resource):
    # returns lists created by a specific user
    # TODO: implement sort options like newest, oldest or most liked
    def get(self, name, page):
        user = User.objects.get(user_name=name)
        list_coll = user.created_lists
        lower, upper = get_slice_bounds(page)

        return jsonify(list_coll.rank_lists[lower:upper])
