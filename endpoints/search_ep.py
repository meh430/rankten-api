from flask import Response, request, jsonify
from flask_restful import Resource
from database.models import User, RankedList
from errors import *
from database.db import get_slice_bounds

# /search_users/<page>/<sort>
# supports GET


class SearchUsersApi(Resource):

    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):
        query = request.args.get('q')
        result = User.objects(user_name__icontains=query).only(
            'user_name', 'rank_points', 'prof_pic').order_by(sort_options[sort] if sort != LIKES_DESC else '-rank_points')
        lower, upper = get_slice_bounds(page, 100)

        list_len = len(result)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper

        return jsonify(result[lower:upper])

# /search_lists/<page>/<sort>
# supports GET


class SearchListsApi(Resource):
    # TODO: Query the contents of the list as well
    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):
        query = request.args.get('q')
        query = query.replace('+', ' ')

        result = RankedList.objects(
            title__icontains=query).order_by(sort_options[sort])
        lower, upper = get_slice_bounds(page)
        result = list(result)
        list_len = len(result)
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper

        return jsonify(result[lower:upper])
