from flask import Response, request, jsonify
from database.models import RankedList, User
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

# like/unlike post
# check if user in liked list or not
# like: +1 num likes, add user to like list, add points to owner of the ranked list
# unlike: -1 num likes, rm user from like list, rm points from owner of the ranked list


class LikeApi(Resource):
    @jwt_required
    def post(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        curr_list = RankedList.objects.get(id=id)
        like_list = curr_list.liked_users
        list_owner = curr_list.created_by

        exec_like = user not in like_list

        if exec_like:
            curr_list.update(num_likes=curr_list.num_likes +
                             1, push__liked_users=user)
            list_owner.update(rank_points=list_owner.rank_points+1)
        else:
            curr_list.update(num_likes=curr_list.num_likes -
                             1, pull__liked_users=user)
            list_owner.update(rank_points=list_owner.rank_points - 1)

        return ('liked list' if exec_like else 'unliked list'), 200
