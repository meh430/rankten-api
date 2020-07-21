class RankItem:
    def __init__(self, parent_title, item_name, rank, description=None, picture=None):
        self.parent_title = parent_title
        self.item_name = item_name
        self.rank = rank
        self.description = description
        self.picture = picture

    def to_dict(self):
        rankItem = {}
        rankItem['parent_title'] = self.parent_title
        rankItem['item_name'] = self.item_name
        rankItem['rank'] = self.rank
        if self.description:
            rankItem['description'] = self.description
        if self.picture:
            rankItem['picture'] = self.picture

        return rankItem
