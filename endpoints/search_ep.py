from flask import Response, request, jsonify
from flask_restful import Resource
from database.models import User, RankedList
from errors import sort_options, check_ps
from database.db import get_slice_bounds


class SearchUsersApi(Resource):
    @check_ps
    def get(self, page, sort):
        query = request.args.get('q')
        result = User.objects(user_name__icontains=query).only(
            'user_name', 'rank_points', 'prof_pic').order_by(sort_options[sort])
        lower, upper = get_slice_bounds(page)
        result = list(result)
        list_len = len(result)
        if lower >= list_len:
            return 'Invalid page', 400
        upper = list_len if upper >= list_len else upper

        return jsonify(result[upper:lower])


class SearchListsApi(Resource):
    # TODO: Query the contents of the list as well
    @check_ps
    def get(self, page, sort):
        query = request.args.get('q')
        query = query.replace('+', ' ')

        result = RankedList.objects(
            title__icontains=query).order_by(sort_options[sort])
        lower, upper = get_slice_bounds(page)
        result = list(result)
        list_len = len(result)
        if lower >= list_len:
            return 'Invalid page', 400
        upper = list_len if upper >= list_len else upper

        return jsonify(result[upper:lower])
