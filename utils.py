sort_options = {0: '-num_likes', 1: '-date_created', 2: '+date_created'}
LIKES_DESC, DATE_DESC, DATE_ASC = 0, 1, 2

def get_slice_bounds(page, num_items=10):
    upper = int(page) * num_items
    lower = upper - num_items
    return (lower, upper)

def sort_list(documents, sort, user=False):
    if sort == LIKES_DESC:
        if user:
            documents = sorted(documents, key=lambda k: k['rank_points'], reverse=True)
        else:
            documents = sorted(documents, key=lambda k: k['num_likes'] if isinstance(
                k, dict) else k.num_likes, reverse=True)
    elif sort == DATE_DESC:
        documents = sorted(
            documents, key=lambda k: k['date_created']['$date'] if isinstance(k, dict) else k.date_created, reverse=True)
    elif sort == DATE_ASC:
        documents = sorted(
            documents, key=lambda k: k['date_created']['$date'] if isinstance(k, dict) else k.date_created, reverse=False)

    return documents

def validate_bounds(list_len, page, num_items=10):
    lower, upper = get_slice_bounds(page, num_items)
    if lower >= list_len:
        return tuple(())

    upper = list_len if upper >= list_len else upper
    return (lower, upper)


def slice_list(documents, page, num_items=10):
    bounds = validate_bounds(len(documents), page, num_items)
    if len(bounds) == 0:
        return ['Trying to access a page that does not exist']
 
    return documents[bounds[0]:bounds[1]]

def get_compact_uinfo(user_list):
    return [{'user_name': f.user_name, 'prof_pic': f.prof_pic, 'bio': f.bio if len(f.bio) <= 50 else (f.bio[:47]+'...'), 'rank_points': f.rank_points} for f in user_list]

#custom schema for list card elements
def ranked_list_card(lists):
    if not lists or isinstance(lists[0], str):
        return lists
    ranked_list_cards = []
    for ranked_list in lists:
        r_card = {
            '_id': str(ranked_list.id),
            'user_name': ranked_list.user_name, 
            'prof_pic': ranked_list.created_by.prof_pic, 
            'title': ranked_list.title, 
            'date_created': {'$date': int(ranked_list.date_created.timestamp())}, 
            'num_likes': ranked_list.num_likes, 
            'num_comments': ranked_list.num_comments}
        r_items_preview = []
        pic = ""
        
        for r_item in ranked_list.rank_list:
            if pic == "" and r_item.picture != "":
                pic = r_item.picture
            if len(r_items_preview) < 3:
                r_items_preview.append({
                    'item_name': r_item.item_name,
                    'rank': r_item.rank
                })
            
            if pic != "" and len(r_items_preview) >= 3:
                break

        
        list_comments = ranked_list.comment_section.comments
        has_comments = ranked_list.num_comments > 0
        if has_comments:
            r_card['comment_preview'] = {
                'comment': list_comments[0].comment,
                'prof_pic': list_comments[0].prof_pic,
                'user_name': list_comments[0].user_name,
                'date_created': int(list_comments[0].date_created.timestamp())
            }
        
        r_card['rank_list'] = r_items_preview
        r_card['num_rank_items'] = len(ranked_list.rank_list)
        r_card['picture'] = pic
        ranked_list_cards.append(r_card)
    
    return ranked_list_cards