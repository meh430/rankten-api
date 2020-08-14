sort_options = {0: '-num_likes', 1: '-date_created', 2: '+date_created'}
LIKES_DESC, DATE_DESC, DATE_ASC = 0, 1, 2

def get_slice_bounds(page, num_items=50):
    upper = int(page) * num_items
    lower = upper - num_items
    return (lower, upper)

def sort_list(documents, sort):
    print("SORTINGNGJEFIOSJOIJD")
    if sort == LIKES_DESC:
        documents = sorted(documents, key=lambda k: k['num_likes'] if isinstance(
            k, dict) else k.num_likes, reverse=True)
    elif sort == DATE_DESC:
        documents = sorted(
            documents, key=lambda k: k['date_created']['$date'] if isinstance(k, dict) else k.date_created, reverse=True)
    elif sort == DATE_ASC:
        documents = sorted(
            documents, key=lambda k: k['date_created']['$date'] if isinstance(k, dict) else k.date_created, reverse=False)

    return documents


def slice_list(documents, page):
    list_len = len(documents)
    lower, upper = get_slice_bounds(page)
    if lower >= list_len:
        return ['Trying to access a page that does not exist']
    upper = list_len if upper >= list_len else upper

    return documents[lower:upper]

def get_compact_uinfo(user_list):
    return [{'user_name': f.user_name, 'prof_pic': f.prof_pic, 'bio': f.bio if len(f.bio) <= 50 else (f.bio[:47]+'...')} for f in user_list]

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
                'user_name': list_comments[0].user_name
            }
        
        r_card['rank_list'] = r_items_preview
        r_card['picture'] = pic
        ranked_list_cards.append(r_card)
    
    return ranked_list_cards