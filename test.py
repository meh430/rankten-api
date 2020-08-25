import random
import requests
num_posts = 60
user = {'user_name': 'meh4life', 'password': 'pword', 'token': 'token'}

user['token'] = requests.post(url='http://localhost:5000/login',  headers={'User-agent': 'test bot 1.0'}, json=user).json()['jwt_token']

for i in range(num_posts):
    ranked_list = {'title': f'topic title {i}'}
    num_items = random.randint(2, 11)
    r_items = [{'item_name': f'topic {i} item {j}', 'rank': j,
                'description': 'description for item {j}'} for j in range(1, num_items)]
    ranked_list['rank_list'] = list(r_items)
    print(requests.post(url='http://192.168.0.22:5000/rankedlist', headers={
        'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {user['token']}"}, json=ranked_list).json())