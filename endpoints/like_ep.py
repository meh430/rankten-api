from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from database.json_cacher import *
from errors import *
from endpoints.comment_ep import comment_parent_id
from utils import *
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
            curr_list.update(push__liked_users=user,
                             num_likes=len(curr_list.liked_users)+1)
            list_owner.update(inc__rank_points=1)
            user_list_coll.update(push__liked_lists=curr_list)
        else:
            curr_list.update(pull__liked_users=user,
                             num_likes=len(curr_list.liked_users)-1)
            list_owner.update(dec__rank_points=1)
            user_list_coll.update(pull__liked_lists=curr_list)

        #JsonCache.delete(id, LIKED_USERS)
        #JsonCache.delete(uid, LIKED_LISTS)
        #JsonCache.sort_delete(list_owner.user_name, USER_LISTS)
        JsonCache.bulk_delete(
            key_dict(key=id, itemType=LIKED_USERS),
            key_dict(key=uid, itemType=LIKED_LISTS),
            key_dict(key=list_owner.user_name, itemType=USER_LISTS),
            key_dict(key=list_owner.user_name, itemType=USER_LISTSP)
        )

        return {'message': ('liked list' if exec_like else 'unliked list')}, 200

    # returns list of users that liked a list
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])
        
        liked_users = []
        if not refresh and JsonCache.exists(key=id, itemType=LIKED_USERS):
            liked_users = JsonCache.get_item(key=id, itemType=LIKED_USERS)
        else:
            liked_users = get_compact_uinfo(
                RankedList.objects.get(id=id).liked_users)
            JsonCache.cache_item(key=id, item=liked_users, itemType=LIKED_USERS)

        return liked_users, 200

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
            comment.update(push__liked_users=user,
                           num_likes=len(comment.liked_users)+1)
            comment.made_by.update(inc__rank_points=1)
        else:
            comment.update(pull__liked_users=user,
                           num_likes=len(comment.liked_users)-1)
            comment.made_by.update(dec__rank_points=1)


        #JsonCache.sort_delete(comment_parent_id(id), LIST_COMMENTS)
        #JsonCache.sort_delete(comment.made_by.user_name, USER_COMMENTS)
        JsonCache.bulk_delete(
            key_dict(key=comment_parent_id(id), itemType=LIST_COMMENTS),
            key_dict(key=comment.made_by.user_name, itemType=USER_COMMENTS)
        )
        return {'message': ('liked comment' if exec_like else 'unliked comment')}, 200

# /likes/<page>
# supports GET
class LikedListsApi(Resource):
    # return all the lists liked by a user
    @jwt_required
    @user_does_not_exist_error
    @schema_val_error
    def get(self, page: int, sort: int):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        page = int(page)
        sort = int(sort)
        if page <= 0:
            raise InvalidPageError
        
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        if 'ids' in request.args and request.args['ids']:
            return [str(r_list.id) for r_list in user.created_lists.liked_lists]

        liked_lists = []
        if not refresh and JsonCache.exists(key=uid, itemType=LIKED_LISTS, page=page, sort=sort):
            liked_lists = JsonCache.get_item(key=uid, itemType=LIKED_LISTS, page=page, sort=sort)
        else:
            liked_lists = user.created_lists.liked_lists
            bounds = validate_bounds(len(liked_lists), page)
            if not bounds:
                raise InvalidPageError
            
            liked_lists = ranked_list_card(liked_lists[bounds[0]:bounds[1]])
            liked_lists = sort_list(liked_lists, sort)
            JsonCache.cache_item(key=uid, item=liked_lists, itemType=LIKED_LISTS, page=page, sort=sort)

        return liked_lists, 200