from flask import Response, request, jsonify
from database.models import RankedList
from flask_restful import Resource
from database.db import get_slice_bounds
from errors import check_ps


class DiscoverApi(Resource):

    @check_ps
    def get(self, page: int, sort: int):
        lower, upper = get_slice_bounds(page)
        all_lists = RankedList.objects().order_by(sort_options[sort])
        list_len = RankedList.objects.count()
        if lower >= list_len:
            return 'Invalid page', 400
        upper = list_len if upper >= list_len else upper
        return jsonify(all_lists[lower:upper])
