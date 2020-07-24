import requests
import random


class RankItem:
    def __init__(self, item_name, rank, description=None, picture=None):
        self.item_name = item_name
        self.rank = rank
        self.description = description
        self.picture = picture

    def to_dict(self):
        rankItem = {}
        rankItem['item_name'] = self.item_name
        rankItem['rank'] = self.rank
        if self.description:
            rankItem['description'] = self.description
        if self.picture:
            rankItem['picture'] = self.picture

        return rankItem


# create some users and store returned jwt tokens
# have other users follow one user
# create some posts for each person

# like some posts
# add something to some posts
# get everyone who has liked a certain post
# get all liked posts and all created posts
# delete all posts


user_data = [
    {
        'user_name': 'meh',
        'password': 'password1'
    },
    {
        'user_name': 'anj25',
        'password': 'password2'
    },
    {
        'user_name': 'i_shit_a',
        'password': 'password3'
    },
    {
        'user_name': 'manj50',
        'password': 'password4'
    },
    {
        'user_name': 'vijpi',
        'password': 'password5'
    },
    {
        'user_name': 'ansh404',
        'password': 'password6'
    },
    {
        'user_name': 'vin_china',
        'password': 'password7'
    }
]

tokens = dict({})

for user in user_data:
    tokens[user['user_name']] = requests.post(
        url='http://localhost:5000/signup', headers={'User-agent': 'test bot 1.0'}, json=user).json()['jwt_token']
print('done creating users')

for user in user_data:
    if user['user_name'] != 'meh':
        requests.post(url='http://localhost:5000/follow/meh', headers={
                      'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json={})
print('done following')

data_topics = ['Xbox Games', 'PLaystation Games', 'Phones', 'Anime', 'Horror Movies', 'Comedy Movies', 'World Leaders',
               'Actors', 'Plants', 'Colors', 'Fruits', 'Companies', 'Books', 'Shoes', 'Watches', 'YouTubers', 'TV Shows',
               'Languages', 'Programming Languages', 'Vacation Spots', 'Animals']


def get_list(topics):
    ret = []
    for topic in topics:
        item_no = random.randint(1, 10)
        rank_items = []
        for i in range(1, item_no + 1):
            rank_items.append(RankItem(
                item_name=f'{topic}{i}', rank=i, description=f'Description of {topic} number {i}').to_dict())

        ret.append({
            'title': topic,
            'rank_items': rank_items
        })

    return ret


rank_data = dict({})

for i in range(0, len(data_topics), 3):
    user = user_data[i//3]
    rank_data[user['user_name']] = get_list(data_topics[i: i + 3])
print(rank_data)
for user in user_data:
    ranking_lists = rank_data[user['user_name']]
    for rli in ranking_lists:
        requests.post(url='http://localhost:5000/rankedlist', headers={
                      'User-agent': 'test bot 1.0', 'Authorization': f"Bearer {tokens[user['user_name']]}"}, json=rli)

print('Done creating posts')
