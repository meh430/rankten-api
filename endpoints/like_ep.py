from flask import Response, request, jsonify
from database.models import RankedList, User
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_slice_bounds


class LikeApi(Resource):
    # like/unlike a post
    @jwt_required
    def post(self, id):
        # get curr user info
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        user_list_coll = user.created_lists

        # get list info
        curr_list = RankedList.objects.get(id=id)
        list_owner = curr_list.created_by

        # like if the list is not in user's liked list
        exec_like = curr_list not in user_list_coll.liked_lists

        if exec_like:
            curr_list.update(inc__num_likes=1, push__liked_users=user)
            list_owner.update(inc__rank_points=1)
            user_list_coll.update(push__liked_lists=curr_list)
        else:
            curr_list.update(dec__num_likes=1, pull__liked_users=user)
            list_owner.update(dec__rank_points=1)
            user_list_coll.update(pull__liked_lists=curr_list)

        return ('liked list' if exec_like else 'unliked list'), 200

    # returns list of users that liked a list
    def get(self, id):
        curr_list = RankedList.objects.get(id=id)
        like_list = []
        for liker in curr_list.liked_users:
            like_list.append({'user_name': liker.user_name})

        return jsonify(like_list)


class LikedListsApi(Resource):
    # return all the lists liked by a user
    # TODO: implement sort options like newest, oldest or most liked
    def get(self, name, page):
        user = User.objects.get(user_name=name)
        list_coll = user.created_lists
        lower, upper = get_slice_bounds(page)
        return jsonify(list_coll.liked_lists[lower:upper])
