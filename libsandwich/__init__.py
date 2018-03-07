import requests
import sys
import json
from typing import Dict, List

BASE_URL: str = 'https://www.quartonet.nl/ESAshop'


class Item:
    def __init__(self, item: Dict):
        self.id: int = item['id']
        self.name: str = item['omschr']
        self.price: int = item['prijs']

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '''
    ID: {}
    Name: {}
    Price: {}
    '''.format(self.id, self.name, self.price)


class Sandwich:
    def __init__(self, username: str, password: str):
        self.session = requests.session()

        data = {
            'Password': password,
            'Username': username,
            'ReturnTo': '/ESAshop/'
        }
        response = self.session.post(
            BASE_URL + '/Account/Login',
            data=data
        )

        if response.status_code != 200:
            sys.exit("FATAL: Could not log in")

    def add_to_basket(self, item: Item, amount: int):
        url: str = BASE_URL + '/Bestelling/AddToCart'
        data = {
            'aantal': amount,
            'artikelnr': item.id,
            'gebruikerid': 1497,
            'prijs': item.price
        }
        response = self.session.post(url, data=data)

        if response.status_code != 200:
            print(response)

    def get_shop_cart(self) -> Dict:
        url: str = BASE_URL + '/Artikelen/getShopCartJson'
        response = self.session.get(url)
        return response.json()

    def remove_item_from_shopping_cart(self, item: Item):
        url: str = BASE_URL + '/Bestelling/deleteFromCart'
        data = {
            'artikelnr': item.id,
            'userid': 1497
        }

        response = self.session.post(
            url,
            data=data
        )

        if response.status_code != 200:
            print(response)

    def empty_cart(self):
        items = self.get_shop_cart()
        for item in items:
            self.remove_item_from_shopping_cart(item['nummer'])

    def get_item(self, id: int) -> Item:
        url: str = BASE_URL + '/Artikelen/getArtikel/{}'.format(id)

        response = self.session.get(url)
        try:
            return Item(response.json())
        except json.decoder.JSONDecodeError:
            return None

    def get_all_item_ids(self) -> List[int]:
        url: str = BASE_URL + '/Artikelen/Autocompletebox'
        response = self.session.get(url)
        return [item['value'] for item in response.json()]

    def get_items(self) -> List[Item]:
        items: List[Item] = [self.get_item(item)
                             for item in self.get_all_item_ids()]
        return [item for item in items if item is not None]
