from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import RankedList, User, ListCollection
from .routes import get_slice_bounds
# manipulate a list


class RankedListApi(Resource):
    # get specified list data
    def get(self, id):
        return Response(RankedList.objects.get(id=id).to_json(), mimetype='application/json', status=200)

    # update specified list
    @jwt_required
    def put(self, id):
        # create post, add user to post, add post to list collection of user
        body = request.get_json()
        RankedList.objects.get(id=id).update(**body)
        return 'Updated ranked list', 200

    # delete specified list
    @jwt_required
    def delete(self, id):
        uid = get_jwt_identity()
        ranked_list = RankedList.objects.get(id=id, created_by=uid)
        ranked_list.delete()
        return 'Deleted ranked list', 200


class RankedListsApi(Resource):
    # create new list
    @jwt_required
    def post(self):
        # create post, add user to post, add post to list collection of user
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        new_list = RankedList(**body, created_by=user)
        new_list.save()
        user.created_lists.update(push__rank_lists=new_list)
        user.created_lists.save()
        return {'id': str(new_list.id)}, 200


class UserRankedListsApi(Resource):
    # returns lists created by a specific user
    def get(self, name, page):
        user = User.objects.get(user_name=name)
        list_coll = user.created_lists
        lower, upper = get_slice_bounds(page)

        return Response(jsonify(list_coll.rank_lists[lower:upper]), mimetype='application/json', status=200)
