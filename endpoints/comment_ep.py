from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from database.db import cache, get_slice_bounds
from database.json_cacher import *
from errors import *
import simdjson as json

# /comment/<id>
# supports GET(comment id), POST(list id), PUT(comment id), DELETE(comment id)


@list_does_not_exist_error
@schema_val_error
def comment_parent_id(id):
    return str(Comment.objects.get(id=id).belongs_to.belongs_to.id)


class CommentApi(Resource):

    # get the list that the comment is on
    @comment_does_not_exist_error
    @schema_val_error
    def get(self, id):
        # id here is comment id
        # get the comment section it belongs to and then get the list the comment section belongs to
        rank_list = Comment.objects.get(id=id).belongs_to.belongs_to
        return rank_list.to_json(), 200

    # create a new comment on a specifed list
    @jwt_required
    @list_does_not_exist_error
    @schema_val_error
    def post(self, id):
        # id here is list id
        body = request.get_json()
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        if 'user_name' not in body:
            body['user_name'] = user.user_name

        if 'prof_pic' not in body:
            body['prof_pic'] = user.prof_pic

        if 'edited' in body:
            body['edited'] = False

        rank_list = RankedList.objects.get(id=id)
        comment = Comment(**body, made_by=user,
                          belongs_to=rank_list.comment_section)
        comment.save()
        rank_list.update(num_comments=(
            len(rank_list.comment_section.comments)+1))
        rank_list.comment_section.update(push__comments=comment)
        user.update(inc__num_comments=1)

        JsonCache.delete(user.user_name + USER_COMMENTS)
        JsonCache.delete(id + LIST_COMMENTS)
        return {'_id': str(comment.id)}, 200

    # update a specified comment
    @jwt_required
    @comment_update_error
    @schema_val_error
    def put(self, id):
        # id here is comment id
        body = request.get_json()
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        comment = Comment.objects.get(id=id, made_by=uid)
        if 'edited' not in body or ('editied' in body and not body['edited']):
            body['edited'] = True

        comment.update(**body)
        JsonCache.delete(user.user_name + USER_COMMENTS)
        JsonCache.delete(comment_parent_id(id) + LIST_COMMENTS)
        return 'Updated comment', 200

    # delete a specified comment
    @jwt_required
    @comment_delete_error
    @schema_val_error
    def delete(self, id):
        # id here is comment id
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        comment = Comment.objects.get(id=id, made_by=uid)
        rank_list = comment.belongs_to.belongs_to
        rank_list.update(num_comments=(
            len(rank_list.comment_section.comments)-1))
        comment.delete()
        user.update(dec__num_comments=1)
        JsonCache.delete(user.user_name + USER_COMMENTS)
        JsonCache.delete(comment_parent_id(id) + LIST_COMMENTS)
        return 'Deleted comment', 200

# /comments/<id>/<page>/<sort>
# supports GET(list id)


class CommentsApi(Resource):
    # returns all the comments made on a specified list
    @check_ps
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id, page: int, sort: int):
        limit = int(request.args.get('limit'))
        rank_list_comments = []
        if JsonCache.exists(id + LIST_COMMENTS):
            rank_list_comments = JsonCache.get_item(id + LIST_COMMENTS)
        else:
            rank_list_comments = RankedList.objects.get(
                id=id).comment_section.comments
            JsonCache.cache_item(id + LIST_COMMENTS, rank_list_comments)

        if sort == LIKES_DESC:
            rank_list_comments = sorted(
                rank_list_comments, key=lambda k: k.num_likes, reverse=True)
        elif sort == DATE_DESC:
            rank_list_comments = sorted(
                rank_list_comments, key=lambda k: k.date_created, reverse=True)
        elif sort == DATE_ASC:
            rank_list_comments = sorted(
                rank_list_comments, key=lambda k: k.date_created, reverse=False)

        list_len = len(rank_list_comments)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        upper = (lower+limit) if (lower+limit) <= upper else upper
        return jsonify(rank_list_comments[lower:upper])

# /user_comments/<name>/<page>/<sort>
# supports GET


class UserCommentsApi(Resource):
    # returns all the comments made by a user
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str, page: int, sort: int):
        user_comments = []
        if JsonCache.exists(name + USER_COMMENTS):
            user_comments = JsonCache.get_item(name + USER_COMMENTS)
        else:
            user_comments = Comment.objects(
                user_name=name).order_by(sort_options[sort])
            JsonCache.cache_item(name + USER_COMMENTS, user_comments)
        list_len = len(user_comments)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        return jsonify(user_comments[lower:upper])
