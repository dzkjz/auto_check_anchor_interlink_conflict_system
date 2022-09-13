from wsgiref import headers

import requests
import xml.etree.ElementTree as ET
import re


def get_sitemap():
    response = requests.get("https://www.kucoin.com/ja/main-sitemap.xml", headers={"Accept": "application/json"})

    data = response.text
    url = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'

    pattern = re.compile(url)
    res = pattern.finditer(data)

    for r in res:
        print(r.group(0))


def get_trading_bot_pro():
    trading_bot_spot = 'https://www.kucoin.com/_api_robot/cloudx-scheduler/professional/web/tick?lang=en_US&_ts=1662393172793'
    trading_bot_futures = 'https://www.kucoin.com/_api_robot/cloudx-scheduler/professional/web/futures/symbols?lang=en_US&_ts=1662392890994'

    response = requests.get(trading_bot_futures, headers={"Accept": "application/json"})

    data = response.json()
    pairs = data['data']['all']
    futures_grids = []
    for pair in pairs:
        if pair['symbolCode'] not in futures_grids:
            futures_grids.append(pair['symbolCode'])

    response = requests.get(trading_bot_spot, headers={"Accept": "application/json"})
    data = response.json()
    groups = data['data']['symbol']

    symbols = groups.keys()
    spot_grids = []
    for symbol in symbols:
        pairs = groups[symbol]
        for pair in pairs:
            if pair['symbolCode'] not in spot_grids:
                spot_grids.append(pair['symbolCode'])

    for futures_grid in futures_grids:
        print(f"https://www.kucoin.com/trading-bot/futures/grid/{futures_grid}")

    for spot_grid in spot_grids:
        print(f"https://www.kucoin.com/trading-bot/spot/grid/{spot_grid}")


def get_earn():
    earn_trade = 'https://www.kucoin.com/_pxapi/pool-staking/products?pageSize=1000&currency=&purchasable=0&type=&with_all_up=0&keyword=&with_lockdrop=1&with_polka_fund=1&lang=en_US'
    response = requests.get(earn_trade, headers={"Accept": "application/json"})
    data = response.json()
    items = data['items']
    for item in items:
        url_sub = f'''{item['currency']}/{item['id']}'''
        print(url_sub)


get_trading_bot_pro()
