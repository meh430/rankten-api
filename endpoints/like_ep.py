from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_slice_bounds
from database.models import *
from errors import *


class LikeApi(Resource):
    # like/unlike a post
    @jwt_required
    @list_does_not_exist_error
    @schema_val_error
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
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id):
        curr_list = RankedList.objects.get(id=id)
        return jsonify([{'user_name': liker.user_name, 'prof_pic': liker.prof_pic, 'rank_points': liker.rank_points} for liker in curr_list.liked_users])


class LikeCommentApi(Resource):
    @jwt_required
    @comment_does_not_exist_error
    @schema_val_error
    def post(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        comment = Comment.objects.get(id=id)

        exec_like = user not in comment.liked_users
        if exec_like:
            comment.update(inc__num_likes=1, push__liked_users=user)
            comment.made_by.update(inc__rank_points=1)
        else:
            comment.update(dec__num_likes=1, pull__liked_users=user)
            comment.made_by.update(dec__rank_points=1)

        return ('liked comment' if exec_like else 'unliked comment'), 200


class LikedListsApi(Resource):
    # return all the lists liked by a user
    @jwt_required
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    def get(self, page: int, sort: int):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        liked_lists = []
        if sort == 0:
            liked_lists = sorted(user.created_lists.liked_lists,
                                 key=lambda k: k.num_likes, reverse=True)
        elif sort == 1:
            liked_lists = sorted(user.created_lists.liked_lists,
                                 key=lambda k: k.date_created, reverse=True)
        elif sort == 2:
            liked_lists = sorted(user.created_lists.liked_lists,
                                 key=lambda k: k.date_created, reverse=False)
        list_len = len(liked_lists)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        return jsonify(liked_lists[lower:upper])
