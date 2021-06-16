import json
import re
import time
import requests

from random import randrange
from time import sleep
from typing import Union
from bs4 import BeautifulSoup
from settings import URL, HEADERS

start_time = time.monotonic()

_url = URL
_headers = HEADERS


def parse() -> None:
    """main func"""
    response = requests.get(_url, headers=_headers)
    assert response.status_code == 200

    _soup = BeautifulSoup(response.text, 'lxml')

    categories = {}
    count = 1
    for element in _soup.find_all(class_='mzr-tc-group-item-href'):
        text = element.text
        href = 'https://health-diet.ru' + element.get('href')
        categories[text] = href
        _parse_by_category(name=text, link=href)
        sleep(randrange(1, 2))
        print(f'итерация {count}...')
        count += 1

    _save_data(categories, 'ALL_CATEGORIES')


def _parse_by_category(name: str, link: str) -> None:
    name = _slugify(name)

    response = requests.get(link, headers=_headers)
    _soup = BeautifulSoup(response.text, 'lxml')

    alert_block = _soup.find(class_='uk-alert-danger')
    if alert_block is not None:
        return None

    products_for_json = []
    #  разбираем дом тегов
    products_data = _soup.find(class_='mzr-tc-group-table').find('tbody').find_all('tr')
    for element in products_data:
        product = element.find_all('td')

        title = product[0].find('a').text
        calories = product[1].text
        proteins = product[2].text
        fats = product[3].text
        carbohydrates = product[4].text

        products_for_json.append(
            {
                'title': title,
                'calories': calories,
                'proteins': proteins,
                'fats': fats,
                'carbohydrates': carbohydrates,
            }
        )

    _save_data(products_for_json, name)


def _save_data(data: Union[list, dict], file_name: str) -> None:
    with open(f'data/{file_name}.json', 'a', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def _slugify(text: str) -> str:
    text = text.lower()
    return re.sub(r'[\W-]+', '_', text)


if __name__ == '__main__':
    parse()

print(time.monotonic() - start_time)
