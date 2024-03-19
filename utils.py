import base64
import json
import os
import time
import random
from urllib.parse import urljoin

import requests
from decimal import Decimal

from db.models import Category

main_url = 'https://shop.kz/'


def reload_request(s, method, url, data=None, params=None):
    try:
        methods = {'GET': s.get, 'POST': s.post}
        r = methods[method](url, data=data, params=params)
        r.raise_for_status()
        delay = random.uniform(1, 3)
        time.sleep(delay)
        return r
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        time.sleep(random.uniform(1, 3))
        return None
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
        time.sleep(random.uniform(1, 3))
        return None


def read_html_file(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
        return html_content


def write_to_file(file_name, data):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            json.dump([], file)
    with open(file_name, 'r') as file:
        existing_data = json.load(file)
    existing_data.append(data)
    with open(file_name, 'w') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)


def convert_to_float(str_):
    numeric_str = ''.join(char for char in str_ if char.isnumeric())
    return Decimal(numeric_str)


def check_url_in_file(url_to_check):
    if not os.path.exists('products_urls.json'):
        with open('products_urls.json', 'w') as file:
            json.dump([], file)
    with open('products_urls.json', 'r') as file:
        json_str = file.read()
    if json_str:
        urls_list = json.loads(json_str)
        if url_to_check in urls_list:
            return True
    return False


def add_url_to_file(file_name, new_url):
    try:
        with open(file_name, 'r') as file:
            json_str = file.read()
    except FileNotFoundError:
        urls_list = []
    else:
        urls_list = json.loads(json_str) if json_str else []
    if new_url not in urls_list:
        urls_list.append(new_url)
    with open(file_name, 'w') as file:
        json.dump(urls_list, file, indent=2)


def read_from_file(file_name):
    with open(file_name, 'r') as f:
        json_str = f.read()
    urls_list = json.loads(json_str) if json_str else []
    return urls_list


def make_img_for_db(image_url):
    image_url = urljoin(main_url, image_url)
    return image_url
    # response = requests.get(image_url)
    # if response.status_code == 200:
    #     return base64.b64encode(response.content).decode('utf-8')


def make_slug_shorter(catalog):
    if catalog.count('-') >= 3:
        catalog = catalog.split('-')
        catalog = '-'.join([catalog[0], catalog[-1]])
        return catalog
    return catalog


def get_category_name(catalog_rus, catalog_url):
    category_name = catalog_url.split('/')
    category_name = [item for item in category_name if item != '']
    catalog_name = make_slug_shorter(category_name[-1])
    category_obj = Category(
        catalog_name=catalog_name,
        catalog_rus=catalog_rus
    )
    return category_obj


def convert_url_to_category_name():
    catalogs_text = ''
    with open('catalogs_urls.json', 'r') as f:
        catalog_urls = json.load(f)
        for catalog_url in catalog_urls:
            catalogs = catalog_url.split('/')
            catalog_name = [catalog for catalog in catalogs if catalog != ''][-1]
            catalogs_text += catalog_name + '\n'
    with open('catalogs.text', 'w') as f:
        f.write(catalogs_text)


if __name__ == '__main__':
    convert_url_to_category_name()