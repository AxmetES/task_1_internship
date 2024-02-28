import json
import logging
import random
import time
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from crud import create_table_product, bulk_insert_products
from utils import reload_request, read_html_file, write_to_file, convert_to_float, check_url_in_file, add_url_to_file, \
    read_from_file


def get_catalog(s, main_url):
    catalogs_urls = []
    r = reload_request(s, 'GET', main_url)
    soup = BeautifulSoup(r.text, 'lxml')
    div_catalog = soup.find('div', class_='catalog-menu__sidebar').find_all('li')[1:-3]
    urls = [x.find('a')['href'] for x in div_catalog]
    for url in urls:
        catalogs_urls.append(urljoin(main_url, url))
    return catalogs_urls


def get_category_name(catalog_url):
    category_name = catalog_url.split('/')
    category_name = [item for item in category_name if item != '']
    return category_name[-1]


def get_product(s, category_name, product_url):
    try:
        r = reload_request(s, 'GET', product_url)
        product_obj = {}
        soup = BeautifulSoup(r.text, 'lxml')
        div_container = soup.find('div', class_='container bx-content-seection')

        title = div_container.find('div', class_='bx-title__container').text.strip()
        product_obj['title'] = title if title else None

        article = div_container.find('ul', class_='bx-card-mark col-lg-4 col-xs-12 col-sm-6').find('li').text.strip()
        product_obj['article'] = article if article else None

        img_url = 'https:' + div_container.find(
            'div',
            class_='bx_bigimages_imgcontainer').find('img').get('data-src') if div_container.find(
            'div',
            class_='bx_bigimages_imgcontainer').find('img') else None
        product_obj['img_url'] = img_url if img_url else None

        product_obj['exist'] = True
        div_exist = div_container.find('div', class_='bx-item-buttons')
        if div_exist:
            product_obj['exist'] = False if (
                    'Увы, этот товар закончился. Посмотритедругие варианты' in
                    [span.get_text(strip=True) for span in div_exist.find_all('span')]) else True
        product_obj['price_list'] = None
        product_obj['price_in_chain_stores'] = None
        product_obj['price_in_the_online_store'] = None
        product_obj['product_price_of_the_week'] = None
        li_price = div_container.find(
            'div',
            class_='bx-more-prices').find_all('li') if div_container.find('div', class_='bx-more-prices') else None
        if li_price:
            price_map = {
                'Цена по прайсу': 'price_list',
                'Цена в магазинах сети': 'price_in_chain_stores',
                'Цена в интернет-магазине': 'price_in_the_online_store',
                'Цена товара недели': 'product_price_of_the_week'
                }
            for price in li_price:
                try:
                    spans = price.find_all('span')
                    product_obj[price_map[spans[0].get_text(strip=True)]] = convert_to_float(spans[1].get_text(strip=True))
                except KeyError as e:
                    logging.exception(e)
                    continue
        divs_details = div_container.find_all('div', class_='bxe-tabs__content')
        div_details = divs_details[0].find_all('div', class_='bx_detail_chars_i') if divs_details[0] else None
        details = {}
        if div_details:
            for div_detail in div_details:
                dt = div_detail.find('dt').get_text(strip=True)
                dd = div_detail.find('dd').get_text(strip=True)
                details[dt] = dd
        product_obj['details'] = json.dumps(details, ensure_ascii=False) if details else None
        product_obj['description'] = divs_details[1].get_text(strip=True) if div_details[1] else None
        product_obj['category_name'] = category_name
        product_obj['url'] = product_url
        product_obj['created_at'] = datetime.now()
        product_obj['updated_at'] = datetime.now()
        return product_obj
    except Exception as e:
        logging.exception(f'{e}, page url:{product_url}')


def get_products(s, category_name, catalog_products_urls):
    product_objs = []
    random.shuffle(catalog_products_urls)
    for product_url in catalog_products_urls:
        product_objs.append(get_product(s, category_name, product_url))
        logging.info(f'Add to db: {product_url}')
        delay = random.uniform(1, 3)
        time.sleep(delay)
    if product_objs:
        bulk_insert_products(product_objs)
        logging.info(f'saved to DB: {product_objs}')
    delay = random.uniform(1, 3)
    time.sleep(delay)


def get_catalog_products(s, catalogs_urls, main_url):
    random.shuffle(catalogs_urls)
    for catalog_url in catalogs_urls:
        category_name = get_category_name(catalog_url)
        r = reload_request(s, 'GET', catalog_url)
        soup = BeautifulSoup(r.text, 'lxml')
        div_pages = soup.find('div', class_='bx-pagination-container row')
        if div_pages:
            div_pages = div_pages.find('ul').find_all('li')
        total_pages = int(div_pages[-2].text) if div_pages else 1
        page = 2
        while True:
            dev_products = [div.find('a')['href'] for div in soup.find_all('div', class_='bx_catalog_item_title')]
            catalog_products_urls = [urljoin(main_url, url) for url in dev_products]
            logging.info(f'current catalog-page: {category_name} - {page}')
            get_products(s, category_name, catalog_products_urls)
            if page > total_pages:
                break
            params = {"PAGEN_1": page}
            r = reload_request(s, 'GET', catalog_url, params=params)
            soup = BeautifulSoup(r.text, 'lxml')
            page += 1


def get_sub_catalog_urls(s, catalog_url, main_url):
    r = reload_request(s, 'GET', catalog_url)
    soup = BeautifulSoup(r.text, 'lxml')
    dev_sub_catalog = soup.find('div', class_='bx_catalog_tile').find_all('li')
    sub_catalogs_urls = [urljoin(main_url, x.find('a')['href']) for x in dev_sub_catalog]
    return sub_catalogs_urls


def main():
    sub_sub_catalogs_urls = []
    try:
        create_table_product()
        main_url = 'https://shop.kz/'
        s = requests.Session()
        s.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        })
        catalogs_urls = get_catalog(s, main_url)
        random.shuffle(catalogs_urls)
        for catalog_url in catalogs_urls:
            sub_catalogs_urls = get_sub_catalog_urls(s, catalog_url, main_url)
            for sub_catalog_url in sub_catalogs_urls:
                sub_sub_catalogs_urls.extend(get_sub_catalog_urls(s, sub_catalog_url, main_url))
                logging.info('len sub_sub_catalogs_urls: f{len(sub_sub_catalogs_urls)}')
                delay = random.uniform(1, 3)
                time.sleep(delay)
        get_catalog_products(s, sub_sub_catalogs_urls, main_url)
        logging.info(f'Parsing finish: {datetime.now().time()}')
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(
        filename="shopkz.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    main()
    # main_url = 'https://shop.kz/'
    # s = requests.Session()
    # s.headers.update({
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     'Accept-Encoding': 'gzip, deflate, br, zstd',
    #     'Accept-Language': 'en-US,en;q=0.9',
    #     'Cache-Control': 'no-cache',
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    # })
    # sub_sub_catalogs_urls = ['https://shop.kz/offers/naushniki-i-garnitury/naushniki-dlya-telefonov/']
    # sub_sub_catalogs_urls = read_from_file('catalogs_urls.json')
    # get_catalog_products(s, sub_sub_catalogs_urls, main_url)