import requests
import random
user_data = [dict({'user_name': f'user_{i}', 'password': f'password_{i}'})
             for i in range(30)]
tokens = dict({})
# create users
for user in user_data:
    response = requests.post(url='http://localhost:5000/signup',  headers={
        'User-agent': 'test bot 1.0'}, json=user).json()
    print(response)
    tokens[user['user_name']] = response['jwt_token']

# follow user 0, 0 follow everyone
for user in user_data:
    if user['user_name'] == 'user_0':
        continue

    print(requests.post(url='http://localhost:5000/follow/user_0', headers={
        'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json={}).json())
    print(requests.post(url=f"http://localhost:5000/follow/{user['user_name']}", headers={
        'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens['user_0']}"}, json={}).json())

# unfollow some users
for i in range(10, 16):
    print(requests.post(url=f'http://localhost:5000/follow/user_{i}', headers={
        'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens['user_0']}"}, json={}).json())

# make 10-30 posts per user
for user in user_data:
    num_posts = random.randint(10, 30)
    for i in range(num_posts):
        ranked_list = dict({'title': f'topic title {i}',
                            'user_name': user['user_name']})
        num_items = random.randint(2, 11)
        r_items = [dict({'item_name': f'topic {i} item {j}', 'rank': j,
                         'description': 'description for item {j}'}) for j in range(1, num_items)]
        ranked_list['rank_list'] = list(r_items)
        print(requests.post(url='http://localhost:5000/rankedlist', headers={
            'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json=dict(ranked_list)).json())
