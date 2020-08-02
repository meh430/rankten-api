from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from errors import *
from database.db import get_slice_bounds


class CommentApi(Resource):
    @list_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def get(self, id):
        # id here is list id
        rank_list_comments = RankedList.objects.get(id=id).comment_section
        return {'num_comments': rank_list_comments.num_comments}, 200

    @jwt_required
    @list_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def post(self, id):
        # id here is list id
        body = request.get_json()
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        if 'user_name' not in body:
            body['user_name'] = user.user_name

        if 'prof_pic' not in body:
            body['prof_pic'] = user.prof_pic

        rank_list_comments = RankedList.objects.get(id=id).comment_section
        comment = Comment(**body, made_by=user, belongs_to=rank_list_comments)
        comment.save()
        rank_list_comments.update(push__comments=comment, inc__num_comments=1)
        return {'_id': comment.id}, 200

    @jwt_required
    @comment_update_error
    @schema_val_error
    @internal_server_error
    def put(self, id):
        body = request.get_json()
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        comment = Comment.objects.get(id=id, made_by=uid)
        if 'edited' not in body or ('editied' in body and not body['edited']):
            body['edited'] = True

        comment.update(**body)
        return 'Updated comment', 200

    @jwt_required
    @comment_delete_error
    @schema_val_error
    @internal_server_error
    def delete(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        comment = Comment.objects.get(id=id, made_by=uid)
        comment_section = comment.belongs_to
        comment.delete()
        comment_section.update(dec__num_comments=1)
        return 'Deleted comment', 200


class CommentsApi(Resource):
    @check_ps
    @list_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def get(self, id, page: int, sort: int):
        rank_list_comments = []
        if sort == 0:
            rank_list_comments = sorted(RankedList.objects.get(
                id=id).comment_section.comments, key=lambda k: k.num_likes, reverse=True)
        elif sort == 1:
            rank_list_comments = sorted(RankedList.objects.get(
                id=id).comment_section.comments, key=lambda k: k.date_created, reverse=True)
        elif sort == 2:
            rank_list_comments = sorted(RankedList.objects.get(
                id=id).comment_section.comments, key=lambda k: k.date_created, reverse=False)

        list_len = len(rank_list_comments)
        lower, upper = get_slice_bounds(page)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        return jsonify(rank_list_comments[lower:upper])
