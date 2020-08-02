from database.db import get_slice_bounds
sort_options = {0: '-num_likes', 1: '-date_created', 2: '+date_created'}


def check_ps(func):
    def wrapper(*args, **kwargs):
        page = int(kwargs['page'])
        sort = int(kwargs['sorg'])
        if page <= 0:
            return 'Invalid page num', 400

        if sort not in sort_options:
            sort = 0

        func(*args, page=page, sort=sort, **kwargs)

    return wrapper
