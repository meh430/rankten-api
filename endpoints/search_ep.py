from flask import Response, request, jsonify
from flask_restful import Resource
from database.models import User, RankedList
from errors import *
from utils import *
# /search_users/<page>/<sort>
# supports GET
class SearchUsersApi(Resource):

    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):
        query = request.args.get('q')
        if not query or " " in query:
            return [], 200


        lower, upper = get_slice_bounds(page, 50)
        list_len = User.objects(user_name__icontains=query).only('user_name', 'rank_points', 'prof_pic').count()
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper

        result = User.objects(user_name__icontains=query).only('user_name', 'rank_points', 'prof_pic').order_by(sort_options[sort] if sort != LIKES_DESC else '-rank_points')[lower:upper]
        return jsonify(result)

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

        lower, upper = get_slice_bounds(page)
        print(get_slice_bounds(page))
        list_len = RankedList.objects(title__icontains=query, private=False).count()
        if list_len == 0:
            return [], 200

        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper

        result = RankedList.objects(title__icontains=query, private=False).order_by(sort_options[sort])[lower:upper]

        return jsonify(ranked_list_card(result))
