import argparse
import logging
import os

import re

from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--urls_txt', default='sample', help='Name of the txt file with urls of items to parse.')
    parser.add_argument('--currency', default='USD', help='Currency to display prices in.')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests in seconds.')
    return parser.parse_args()


def setup_files(args):
    try:
        output_dir = 'output'
        input_file = args.urls_txt
        os.makedirs(output_dir, exist_ok=True)

        output_file_name = (
            f'{output_dir}/'
            f'{input_file.replace(".txt", "")}_'
            f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        )

        with open(f"input/{input_file}", 'r') as file:
            urls = [line.strip() for line in file]

    except (OSError, FileNotFoundError) as e:
        logging.error(f"Error: {e}")
        return

    return output_file_name, urls


def replace_special(url):
    replacements = {
        '%20': ' ', '%22': '\"', '%26': "&",
        '%27': '\'', '%28': '(', '%29': ')',
        '%3A': ':', '%60': '`', '%7C': '|',
    }

    for old, new in replacements.items():
        url = url.replace(old, new)
    return url


def make_request(session, url, headers):
    try:
        r = session.get(url, headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        return


def extract_item_name_id(soup):
    script_tags = soup.find_all('script', type='text/javascript')
    for script_tag in script_tags:
        if script_tag.string:
            match = re.search(r'Market_LoadOrderSpread\(\s*(\d+)\s*\)', script_tag.string)
            if match:
                return match.group(1)
    return None


def get_currency_code(currency_name):
    currency_codes = {
        'USD': 1, 'GBP': 2, 'EUR': 3, 'CHF': 4, 'RUB': 5, 'PLN': 6, 'BRL': 7, 'JPY': 8,
        'NOK': 9, 'IDR': 10, 'MYR': 11, 'PHP': 12, 'SGD': 13, 'THB': 14, 'VND': 15, 'KRW': 16,
        'UAH': 18, 'MXN': 19, 'CAD': 20, 'AUD': 21, 'NZD': 22, 'CNY': 23, 'INR': 24, 'CLP': 25,
        'PEN': 26, 'COP': 27, 'ZAR': 28, 'HKD': 29, 'TWD': 30, 'SAR': 31, 'AED': 32, 'SEK': 33
    }

    if isinstance(currency_name, str):
        return currency_codes.get(currency_name.upper(), 1)
    else:
        return None


def main():
    args = get_args()
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    output_file_name, urls = setup_files(args)
    if output_file_name is None or urls is None:
        return

    logging.info(f"Script started with {len(urls)} items to process.\n")

    ua = UserAgent()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': ua.random
    }

    try:
        with requests.Session() as session:
            with open(output_file_name, 'w') as output_file:
                for i, url in enumerate(urls):
                    item = replace_special(url.split('/')[-1])

                    output_file.write(f'Title: {item}\nUrl: {url}\n')
                    logging.info(f"Processing item: {item}")

                    sleep(0.1)

                    r = make_request(session, url, headers)
                    logging.info(f"Made request to: {url}")

                    sleep(0.1)

                    soup = BeautifulSoup(r.text, 'html.parser')
                    item_name_id = extract_item_name_id(soup)

                    if item_name_id:
                        logging.info(f"Item name id extracted: {item_name_id}")

                        api_url = (
                            f'https://steamcommunity.com/market/itemordershistogram?'
                            f'&language=english'
                            f'&currency={get_currency_code(args.currency)}'
                            f'&item_nameid={item_name_id}'
                        )

                        sleep(0.1)

                        response = make_request(session, api_url, headers)
                        data = response.json()

                        if data is not None and 'success' in data and data['success'] == 1:
                            highest_buy_order = int(data['highest_buy_order']) / 100
                            lowest_sell_order = int(data['lowest_sell_order']) / 100

                            lowest_sell_order_str = f'Lowest sell order: {lowest_sell_order} {args.currency}'
                            highest_buy_order_str = f'Highest buy order: {highest_buy_order} {args.currency}'

                            logging.info(lowest_sell_order_str)
                            logging.info(highest_buy_order_str)

                            output_file.write(lowest_sell_order_str + '\n')
                            output_file.write(highest_buy_order_str + '\n\n')

                            if i < len(urls) - 1:
                                logging.info(f"delaying for {args.delay} second\n")
                                sleep(args.delay)

                        else:
                            logging.error('Failed to fetch price data.')
                    else:
                        logging.error('Failed to extract item name id from the page.')

    except Exception as e:
        logging.error(f'Error: {e}')

    logging.info(f"\nScript finished. Output file: {output_file_name}")


if __name__ == '__main__':
    main()
