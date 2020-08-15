from flask import request, jsonify
from flask_restful import Resource
from database.models import RankedList
from errors import *
from database.json_cacher import *
from utils import *

# /discover/<page>/<sort>
# supports GET
class DiscoverApi(Resource):
    # returns all the lists
    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        all_lists = []

        if not refresh and JsonCache.exists(str(page), DISCOVER_LIST, sort):
            all_lists = JsonCache.get_item(str(page), DISCOVER_LIST, sort)
        else:
            lower, upper = get_slice_bounds(page)
            list_len = RankedList.objects.count()
            if lower >= list_len:
                raise InvalidPageError
            upper = list_len if upper >= list_len else upper
            all_lists = RankedList.objects().order_by(sort_options[sort])[lower:upper]
            all_lists = ranked_list_card(all_lists)
            JsonCache.cache_item(str(page), all_lists, DISCOVER_LIST, sort, hours_in_sec(0.5))
        
        return all_lists, 200
