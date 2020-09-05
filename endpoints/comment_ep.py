from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from database.json_cacher import *
from errors import *
from utils import *

import ujson as json

@list_does_not_exist_error
@schema_val_error
def comment_parent_id(id):
    return str(Comment.objects.get(id=id).belongs_to.belongs_to.id)

# /comment/<id>
# supports GET(comment id), POST(list id), PUT(comment id), DELETE(comment id)
class CommentApi(Resource):

    # get the list that the comment is on
    @comment_does_not_exist_error
    @schema_val_error
    def get(self, id):
        # id here is comment id
        # get the comment section it belongs to and then get the list the comment section belongs to
        return jsonify(Comment.objects.get(id=id).belongs_to.belongs_to)

    """
    schema:
    {
        "comment": string
    }
    """
    # create a new comment on a specifed list
    @jwt_required
    @list_does_not_exist_error
    @schema_val_error
    def post(self, id):
        # id here is list id
        body = request.get_json()
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)

        rank_list = RankedList.objects.get(id=id)
        comment = Comment(**body, edited= False, made_by=user,
                          belongs_to=rank_list.comment_section, 
                          prof_pic=user.prof_pic, user_name=user.user_name)
        comment.save()
        rank_list.update(num_comments=(len(rank_list.comment_section.comments)+1))
        rank_list.comment_section.update(push__comments=comment)
        user.update(inc__num_comments=1)

        #comment was added so some of the cache is invalid
        #delete all comments made by user, all comments on current list, all of the list owner's lists
        JsonCache.bulk_delete(
            key_dict(key=user.user_name, itemType=USER_COMMENTS), 
            key_dict(key=id, itemType=LIST_COMMENTS), 
            key_dict(key=rank_list.user_name, itemType=USER_LISTS),
            key_dict(key=rank_list.user_name, itemType=USER_LISTSP)
        )
        #JsonCache.sort_delete(user.user_name, USER_COMMENTS)
        #JsonCache.sort_delete(id, LIST_COMMENTS)
        #JsonCache.sort_delete(rank_list.user_name, USER_LISTS)

        return json.loads(comment.to_json()), 200

    """
    schema:
    {
        "comment": string
    }
    """
    # update a specified comment
    @jwt_required
    @comment_update_error
    @schema_val_error
    def put(self, id):
        # id here is comment id
        body = request.get_json()
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        Comment.objects.get(id=id, made_by=uid).update(**body, edited=True)

        #comment updated so some of the cache is invalid
        #delete all comments made by user, all comments on current list, all of the list owner's lists
        parent_id = comment_parent_id(id)
        owner_name = RankedList.objects.get(id=parent_id).user_name
        JsonCache.bulk_delete(
            key_dict(key=user.user_name, itemType=USER_COMMENTS),
            key_dict(key=parent_id, itemType=LIST_COMMENTS),
            key_dict(key=owner_name, itemType=USER_LISTS),
            key_dict(key=owner_name, itemType=USER_LISTSP)
        )
        #JsonCache.sort_delete(user.user_name, USER_COMMENTS)
        #JsonCache.sort_delete(parent_id, LIST_COMMENTS)
        #JsonCache.sort_delete(RankedList.objects.get(id=parent_id).user_name, USER_LISTS)

        return json.loads(Comment.objects.get(id=id, made_by=uid).to_json()), 200

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

        JsonCache.bulk_delete(
            key_dict(key=user.user_name, itemType=USER_COMMENTS),
            key_dict(key=str(rank_list.id), itemType=LIST_COMMENTS),
            key_dict(key=rank_list.user_name, itemType=USER_LISTS),
            key_dict(key=rank_list.user_name, itemType=USER_LISTSP)
        )
        #JsonCache.sort_delete(user.user_name, USER_COMMENTS)
        #JsonCache.sort_delete(str(rank_list.id), LIST_COMMENTS)
        #JsonCache.sort_delete(rank_list.user_name, USER_LISTS)

        return {'message': 'Deleted comment'}, 200

# /comments/<id>/<page>/<sort>
# supports GET(list id)
class CommentsApi(Resource):
    # returns all the comments made on a specified list
    @check_ps
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id, page: int, sort: int):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])
        
        rank_list_comments = []
        if not refresh and JsonCache.exists(key=id, itemType=LIST_COMMENTS, sort=sort):
            rank_list_comments = JsonCache.get_item(key=id, itemType=LIST_COMMENTS, sort=sort)
        else:
            rank_list_comments = RankedList.objects.get(id=id).comment_section.comments
            rank_list_comments = sort_list(rank_list_comments, sort)
            JsonCache.cache_item(key=id, item=rank_list_comments, itemType=LIST_COMMENTS, sort=sort)
        
        return jsonify(slice_list(rank_list_comments, page))

# /user_comments/<page>/<sort>
# supports GET
class UserCommentsApi(Resource):
    # returns all the comments made by a user
    @jwt_required
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    def get(self, page: int, sort: int):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])
        
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        name = user.user_name

        user_comments = []
        if not refresh and JsonCache.exists(key=name, itemType=USER_COMMENTS, page=page, sort=sort):
            user_comments = JsonCache.get_item(key=name, itemType=USER_COMMENTS, page=page, sort=sort)
        else:
            bounds = validate_bounds(Comment.objects(user_name=name).count(), page)
            if not bounds:
                raise InvalidPageError
            user_comments = Comment.objects(user_name=name).order_by(sort_options[sort])[bounds[0]:bounds[1]]
            JsonCache.cache_item(key=name, item=user_comments, itemType=USER_COMMENTS, page=page, sort=sort)

        return jsonify(user_comments)