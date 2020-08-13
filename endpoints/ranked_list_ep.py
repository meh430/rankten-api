from flask import Response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import *
from database.db import get_slice_bounds
from errors import *

#custom schema for list card elements
def ranked_list_card(lists):
    ranked_list_cards = []
    for ranked_list in lists:
        r_card = {
            '_id': ranked_list.id,
            'user_name': ranked_list.user_name, 
            'prof_pic': ranked_list.created_by.prof_pic, 
            'title': ranked_list.title, 
            'date_created': ranked_list.date_created, 
            'num_likes': ranked_list.num_likes, 
            'num_comments': ranked_list.num_comments}
        r_items_preview = []
        pic = ""
        for r_item in ranked_list.rank_list:
            if pic == "" and r_item.picture != "":
                pic = r_item.picture
            if len(r_items_preview) <= 3:
                r_items_preview.append({
                    'item_name': r_item.item_name,
                    'rank': r_item.rank
                })
        r_card['rank_list'] = r_items_preview
        r_card['picture'] = pic
        ranked_list_cards.apppend(r_card)
    
    return ranked_list_cards

def json_to_ref(json_list, list_ref, user):
    # convert list of dicts to rankitem refs for bulk updates
    rank_list = []
    for r_item in json_list:
        rank_item = RankItem(**r_item, belongs_to=list_ref, created_by=user)
        rank_item.save()
        rank_list.append(rank_item)
    return rank_list

# /rankedlist/<id>
# supports GET, PUT, DELETE


class RankedListApi(Resource):
    # get specified list data
    @list_does_not_exist_error
    @schema_val_error
    def get(self, id):
        return Response(RankedList.objects.get(id=id).to_json(), mimetype='application/json', status=200)

    # update specified list
    @jwt_required
    @list_update_error
    @schema_val_error
    def put(self, id):
        uid = get_jwt_identity()
        body = request.get_json()
        user = User.objects.get(id=uid)
        curr_list = RankedList.objects.get(id=id, created_by=user)
        curr_list.update(**body)
        return 'Updated ranked list', 200

    # delete specified list
    @jwt_required
    @list_delete_error
    @schema_val_error
    def delete(self, id):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        ranked_list = RankedList.objects.get(id=id, created_by=user)
        ranked_list.delete()
        user.update(dec__list_num=1)
        return 'Deleted ranked list', 200

# /rankedlist
# supports POST


class RankedListsApi(Resource):
    # creates new list
    @jwt_required
    @schema_val_error
    def post(self):
        # create post, add user to post, add post to list collection of user
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        new_list = None
        commentSection = CommentSection()
        commentSection.save()
        rank_list = body.pop('rank_list')
        if 'user_name' in body:
            new_list = RankedList(**body, created_by=user,
                                  comment_section=commentSection)
        else:
            new_list = RankedList(**body, created_by=user,
                                  user_name=user.user_name, comment_section=commentSection)
        new_list.save()
        commentSection.update(belongs_to=new_list)
        if rank_list:
            new_list.update(rank_list=json_to_ref(rank_list, new_list, user))

        user.created_lists.update(push__rank_lists=new_list)
        user.update(inc__list_num=1)
        return {'_id': str(new_list.id)}, 200

# /rankedlists/<name>/<page>/<sort>
# supports GET


class UserRankedListsApi(Resource):
    # returns lists created by a specific user
    @check_ps
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str, page: int, sort: int):
        user = User.objects.get(user_name=name)
        user_lists = user.created_lists.rank_lists
        sort_lists(user_lists, sort)
        
        return jsonify(ranked_list_card(slice_list(user_lists, page)))