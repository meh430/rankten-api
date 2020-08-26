from flask import Response, request, jsonify
from flask_restful import Resource
from database.models import User, RankedList, RankItem
from errors import *
from utils import *
from database.json_cacher import *
# /search_users/<page>/<sort>
# supports GET
class SearchUsersApi(Resource):

    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):

        query = request.args.get('q')
        if not query or " " in query:
            return [], 200
        
        user_bio_query = User.objects.search_text(query)
        user_name_query = User.objects(user_name__icontains=query)
        result = list(user_bio_query)
        result.extend(list(user_name_query))
        result = list(dict.fromkeys(result))

        list_len = len(result)

        if list_len == 0:
            return [], 200

        result = sort_list(result, sort, user=True)
        #result = users_query.only('user_name', 'rank_points', 'prof_pic').order_by(sort_options[sort] if sort != LIKES_DESC else '-rank_points')[lower:upper]
        return jsonify(get_compact_uinfo(slice_list(result, page, num_items=100)))

# /search_lists/<page>/<sort>
# supports GET
class SearchListsApi(Resource):
    # TODO: Query the contents of the list as well
    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):
        query = request.args.get('q')
        query = query.replace('+', ' ')

        if not query:
            return [], 200

        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        result = []
        if not refresh and JsonCache.exists(key=query, itemType=SEARCH_LISTS, sort=sort):
            result = JsonCache.get_item(key=query, itemType=SEARCH_LISTS, sort=sort)
        else: 
            items_query = RankItem.objects(private=False).search_text(query)[:750]
            items_list = [r_list.belongs_to for r_list in items_query]
            result = list(dict.fromkeys(items_list))

            list_len = len(result)
            print(list_len)
            if list_len == 0:
                return [], 200

            result = sort_list(result, sort)
            result = ranked_list_card(result)

            JsonCache.cache_item(key=query, itemType=SEARCH_LISTS, sort=sort, item=result)            


        return slice_list(result, page), 200
