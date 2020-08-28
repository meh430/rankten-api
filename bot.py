import requests
import random
user_data = [dict({'user_name': f'user_{i}', 'password': f'Password#_{i}'})
             for i in range(210, 300)]
tokens = dict({})
# create users
for user in user_data:
    response = requests.post(url='http://192.168.0.22:5000/login',  headers={
        'User-agent': 'test bot 1.0'}, json=user).json()
    print(response)
    tokens[user['user_name']] = response['jwt_token']

# make 10-30 posts per user
for user in user_data:
    num_posts = random.randint(10, 30)
    for i in range(num_posts):
        ranked_list = {'title': f'topic title {i}'}
        num_items = random.randint(2, 11)
        r_items = [{'item_name': f'topic {i} item {j}', 'rank': j,
                    'description': 'description for item {j}'} for j in range(1, num_items)]
        ranked_list['rank_list'] = list(r_items)
        print(requests.post(url='http://192.168.0.22:5000/rankedlist', headers={
            'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json=ranked_list).json())

# have each user make 2 comments on all of a random user's lists
for user in user_data:
    comment_target = random.choice(user_data)
    while comment_target['user_name'] == user['user_name']:
        comment_target = random.choice(user_data)
    target_lists = requests.get(url=f"http://192.168.0.22:5000/rankedlists/{comment_target['user_name']}/1/1", headers={
        'User-agent': 'test bot 1.0'}).json()
    for i in range(2, 10):
        curr_page = requests.get(url=f"http://192.168.0.22:5000/rankedlists/{comment_target['user_name']}/{i}/1", headers={
            'User-agent': 'test bot 1.0'}).json()
        if 'message' in curr_page:
            break
        else:
            target_lists.extend(curr_page)

    for li in target_lists:
        comment1 = {
            'comment': f"comment 1 by {user['user_name']} on {comment_target['user_name']}'s list'"}
        comment2 = {
            'comment': f"comment 2 by {user['user_name']} on {comment_target['user_name']}'s list'"}
        print(requests.post(url=f"http://192.168.0.22:5000/comment/{li['_id']['$oid']}", headers={
            'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json=comment1).json())
        print(requests.post(url=f"http://192.168.0.22:5000/comment/{li['_id']['$oid']}", headers={
            'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json=comment2).json())

# have each user like another random user's lists
for user in user_data:
    like_target = random.choice(user_data)
    while like_target['user_name'] == user['user_name']:
        like_target = random.choice(user_data)
    target_lists = requests.get(url=f"http://192.168.0.22:5000/rankedlists/{like_target['user_name']}/1/1", headers={
        'User-agent': 'test bot 1.0'}).json()
    for i in range(2, 10):
        curr_page = requests.get(url=f"http://192.168.0.22:5000/rankedlists/{like_target['user_name']}/{i}/1", headers={
            'User-agent': 'test bot 1.0'}).json()
        if 'message' in curr_page:
            break
        else:
            target_lists.extend(curr_page)

    for li in target_lists:
        print(requests.post(url=f"http://192.168.0.22:5000/like/{li['_id']['$oid']}", headers={
            'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json={}).json())


print(tokens)
# delete everything at the end?
