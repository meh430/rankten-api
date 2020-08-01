from flask import Response, request, jsonify
from database.models import RankedList
from flask_restful import Resource
from database.db import get_slice_bounds
# 0: most liked, 1: new, 2: old
sort_options = {0: '-num_likes', 1: '-date_created', 2: '+date_created'}


class DiscoverApi(Resource):
    def get(self, page, sort):
        if page <= 0:
            return 'Invalid page num', 400

        if sort not in sort_options:
            sort = 0

        lower, upper = get_slice_bounds(page)
        all_lists = RankedList.objects().order_by(sort_options[sort])
        list_len = len(all_lists)

        if lower >= list_len:
            return 'Invalid page num', 400

        upper = list_len if upper >= list_len else upper

        return jsonify(RankedList.objects[lower:upper])
