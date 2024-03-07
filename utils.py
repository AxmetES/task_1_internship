import base64
import json
import os
import time
import random
from urllib.parse import urljoin

import requests
from decimal import Decimal


main_url = 'https://shop.kz/'


def reload_request(s, method, url, data=None, params=None):
    try:
        methods = {'GET': s.get, 'POST': s.post}
        r = methods[method](url, data=data, params=params)
        r.raise_for_status()
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


def write_to_file(urs, file_name):
    existing_lines = set()
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as existing_file:
            existing_lines = set(line.strip() for line in existing_file)
    existing_lines.update(line.strip() for line in urs)
    with open(file_name, 'w', encoding='utf-8') as temp_file:
        for line in existing_lines:
            temp_file.write(line)
            temp_file.write('\n')


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


def get_category_name(catalog_url):
    category_name = catalog_url.split('/')
    category_name = [item for item in category_name if item != '']
    return category_name[-1]


if __name__ == '__main__':
    s = requests.Session()
    reload_request(s, 'GET', 'http://example.com')