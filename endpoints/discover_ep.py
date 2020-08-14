from flask import request, jsonify
from flask_restful import Resource
from database.models import RankedList
from errors import *
from utils import *

# /discover/<page>/<sort>
# supports GET


class DiscoverApi(Resource):
    # returns all the lists
    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):
        lower, upper = get_slice_bounds(page)
        all_lists = RankedList.objects().order_by(sort_options[sort])
        list_len = RankedList.objects.count()
        if lower >= list_len:
            raise InvalidPageError
        upper = list_len if upper >= list_len else upper
        return jsonify(ranked_list_card(all_lists[lower:upper]))
