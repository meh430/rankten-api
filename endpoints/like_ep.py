from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_slice_bounds
from database.models import *
from errors import *
from endpoints.users_ep import get_compact_uinfo
# /like/<id>
# supports POST, GET


class LikeApi(Resource):
    # like/unlike a list
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
            curr_list.update(push__liked_users=user)
            list_owner.update(inc__rank_points=1)
            user_list_coll.update(push__liked_lists=curr_list)
        else:
            curr_list.update(pull__liked_users=user)
            list_owner.update(dec__rank_points=1)
            user_list_coll.update(pull__liked_lists=curr_list)

        return ('liked list' if exec_like else 'unliked list'), 200

    # returns list of users that liked a list
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id):
        return jsonify(get_compact_uinfo(RankedList.objects.get(id=id).liked_users))

# /like_comment/<id>
# supports POST


class LikeCommentApi(Resource):
    # like/unlike a comment
    @jwt_required
    @comment_does_not_exist_error
    @schema_val_error
    def post(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        comment = Comment.objects.get(id=id)

        exec_like = user not in comment.liked_users
        if exec_like:
            comment.update(push__liked_users=user)
            comment.made_by.update(inc__rank_points=1)
        else:
            comment.update(pull__liked_users=user)
            comment.made_by.update(dec__rank_points=1)

        return ('liked comment' if exec_like else 'unliked comment'), 200

# /likes/<page>/<sort>
# supports GET


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
        if sort == LIKES_DESC:
            liked_lists = sorted(user.created_lists.liked_lists,
                                 key=lambda k: k.num_likes, reverse=True)
        elif sort == DATE_DESC:
            liked_lists = sorted(user.created_lists.liked_lists,
                                 key=lambda k: k.date_created, reverse=True)
        elif sort == DATE_ASC:
            liked_lists = sorted(user.created_lists.liked_lists,
                                 key=lambda k: k.date_created, reverse=False)
        list_len = len(liked_lists)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        return jsonify(liked_lists[lower:upper])
