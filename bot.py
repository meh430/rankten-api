import requests
import random
user_data = [dict({'user_name': f'user_{i}', 'password': f'password_{i}'})
             for i in range(30)]
tokens = dict({})
# create users
for user in user_data:
    tokens[user['user_name']] = requests.post(url='http://localhost:5000/signup',  headers={
        'User-agent': 'test bot 1.0'}, json=user).json()['jwt_token']

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
