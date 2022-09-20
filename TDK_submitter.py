import code
from idlelib import query
from typing import List
from db_handler import database_handler
import pandas
from pandas import DataFrame
import os
import requests
from urllib.parse import urlparse

import json

cookies = [
    'token=e3f9171a2a1188677fec637ef2127448;',
    'admin-gw-v2.kucoin.com_ADMIN-SESSION=0eae080a2a02c6132355a4a9'
]


def price_tokens():
    base_url_price_2 = 'https://www.kucoin.com/_api/currency/v2/prices'
    response = requests.get(base_url_price_2)
    data = response.json()
    keys = json.loads(json.dumps(data['data'])).keys()
    keys = [x.strip() for x in keys]
    print("共发现", len(keys), "个币种")
    return keys


def trade_currency_pairs():
    base_url_trade = 'https://www.kucoin.com/_api/currency/symbols'
    response = requests.get(base_url_trade)
    data = response.json()

    trading_pairs = []
    for item in data['data']:
        code = item['code'].strip()
        symbolCode = item['symbolCode'].strip()
        symbol = item['symbol'].strip()

        if len(code) == 0:
            if len(symbolCode) == 0:
                if len(symbol) == 0:
                    raise ValueError("Invalid symbol")
                else:
                    trading_pairs.append(symbol)
            else:
                trading_pairs.append(symbolCode)
        else:
            trading_pairs.append(code)
    print("有 %s 个币对" % len(trading_pairs))
    return trading_pairs


def deleter(id: str):
    base_url = 'https://nac.kucoin.com:1018/seo-support/tdk/delete?c=&lang=zh_CN'
    headers = {
        "Accept": "application/json",
        "Connection": "keep-alive",
        "Host": "nac.kucoin.com:1018",
        "Cookie": ''.join(cookies),
        "LANG": "zh_CN",
        "requestId": "1661408332951lion.liang"
    }
    body = {
        "id": id
    }
    response = requests.post(base_url, data=body, headers=headers)
    data = response.json()
    if response.status_code == 200 and data['code'] == '200':
        print("Success", data['msg'])


def queryTDKStatus(url: str):
    base_url = 'https://nac.kucoin.com:1018/seo-support/tdk/pageQuery?c=&lang=zh_CN'
    headers = {
        "Accept": "application/json",
        "Connection": "keep-alive",
        "Host": "nac.kucoin.com:1018",
        "Cookie": ''.join(cookies),
        "LANG": "zh_CN",
        "requestId": "1661408332951lion.liang"
    }

    url_parsed = urlparse(url)
    model = url_parsed.path.split("/")[1].replace('/', '', 0)
    branch = url_parsed.path.replace(f'/{model}', '', 1).replace('/', '', 1)
    body = {
        "currentPage": 1,
        "domainName": urlparse(url).netloc,
        "branch": branch,
        "model": model,
        "pageSize": 100
    }
    response = requests.post(url=base_url, json=body, headers=headers)
    data = response.json()

    found_item = None
    if response.status_code == 200 and data['code'] == '200':
        items = data['items']
        for item in items:
            originalUrl = item['originalUrl']
            if originalUrl == url:
                found_item = item
                break
    return found_item


def submitter(url: str, keyword: str, title: str, description: str, page_language="zh_CN"):
    # "en_US"
    base_url = f'https://nac.kucoin.com:1018/seo-support/tdk/add-new?c=&lang=zh_CN'

    headers = {
        "Accept": "application/json",
        "Connection": "keep-alive",
        "Host": "nac.kucoin.com:1018",
        "Cookie": ''.join(cookies),
        "LANG": "zh_CN",
        "operator": "6228451c8f34400006a8de55"
    }
    body = {
        "originalUrl": f"{url}",
        "tdkDetailList": [
            {"language": f"{page_language}", "keyword": f"{keyword}", "title": f"{title}",
             "description": f"{description}"}
        ]
    }

    response = requests.post(base_url, headers=headers, json=body)
    data = response.json()
    print(data)


# {'msg': 'success', 'code': '200', 'data': '62ff5a534233f800010d8c70', 'success': True, 'retry': False}
# usage: submitter(url='https://sandbox.kucoin.com/b', title='a', description='a', keyword='a,b')
# submitter(url='https://sandbox.kucoin.com/b', title='a', description='a', keyword='a,b')


def read_tdks_from_database():
    dh = database_handler()
    tdks = dh.read_tdk_table()

    tdk_templates = []

    for tdk in tdks:
        language_code = tdk[1]
        base_url: str = tdk[2]
        url: str = tdk[3]
        title = tdk[4]
        description = tdk[5]
        keywords = tdk[6]
        token = url.replace(base_url, '')
        if '{0}' in url:
            title = title.replace('{0}', '{token}')
            description = description.replace('{0}', '{token}')
            keywords = keywords.replace('{0}', '{token}')

        tdk_template = {
            'token': token,
            'title': title,
            'description': description,
            'keywords': keywords,
            'language': language_code
        }
        tdk_templates.append(tdk_template)
    return tdk_templates


def updater():
    older_urls = ["https://www.kucoin.com/pt/price/{0}", ]
    for older_url in older_urls:
        item = queryTDKStatus(older_url)
        if item is not None:
            id = item['id']
            originalUrl = item['originalUrl']
            print(originalUrl, id)
            # 删除之前的
            # 只删除那个URL全满足的
            if originalUrl == older_url:
                deleter(id)

    language = 'pt_PT'

    # 创建
    has_template = False

    def customized_tokens_from_template(has_template, token, token_full, language: str):

        if not has_template:
            customized_tokens_template = read_tdks_from_database()

        else:
            customized_tokens_template = {
                'token': token,
                'title': f'Presyo ng {token} | Aktwal na Tsart ng Presyo ng {token} | {token} to USD | KuCoin',
                'description': f"Tingnan ang live chart ng presyo ng {token} upang subaybayan ang mga pagbabago sa presyo sa aktwal na oras. Sundin ang pinakabagong data ng merkado, pagsusuri, at mga social na komento sa KuCoin Crypto Exchange. ",
                'keywords': f'Presyo ng {token}, presyo ng {token}, real-time (live) na tsart ng presyo ng {token}, {token} hanggang USD',
                'language': language
            }

        return customized_tokens_template

    customized_tokens = []
    toks = [
        {
            "coin_name": "Bitcoin",
            "ticker": "BTC"
        },
        {
            "coin_name": "Ethereum",
            "ticker": "ETH"
        }, {
            "coin_name": "Terra Classic",
            "ticker": "LUNC"
        }, {
            "coin_name": "Terra ",
            "ticker": "LUNA"
        }, {
            "coin_name": "TerraClassicUsd",
            "ticker": "USTC"
        }, {
            "coin_name": "Kucoin Token",
            "ticker": "KCS"
        }, {
            "coin_name": "Tron",
            "ticker": "TRX"
        }, {
            "coin_name": "Stellar",
            "ticker": "XLM"
        }, {
            "coin_name": "Usd Coin",
            "ticker": "USDC"
        }, {
            "coin_name": "Algorand",
            "ticker": "ALGO"
        }, {
            "coin_name": "Shiba Inu",
            "ticker": "SHIB"
        }, {
            "coin_name": "Dogecoin",
            "ticker": "DOGE"
        }, {
            "coin_name": "Solana",
            "ticker": "SOL"
        }
    ]

    if has_template:
        for to in toks:
            customized_tokens.append(customized_tokens_from_template(True, to['ticker'], to['coin_name'], language))
    else:
        customized_tokens = customized_tokens_from_template(False, None, None, language)
    price_base_url = 'https://www.kucoin.com/pt/price/'
    tokens = price_tokens()
    ctokens = []
    for ct in customized_tokens:
        ctokens.append(ct['token'])
    for token in tokens:
        print("上传第%s个" % tokens.index(token))
        if token in ctokens:
            token_url = price_base_url + token
            # 检测是否已经存在
            item = queryTDKStatus(token_url)
            # 删除老的
            if item is not None:
                id = item['id']
                originalUrl = item['originalUrl']
                print(originalUrl, id)
                # 删除之前的
                # 只删除那个URL全满足的
                if originalUrl == token_url:
                    deleter(id)

            # 再次检测
            item = queryTDKStatus(token_url)
            if item is None:
                for t in customized_tokens:
                    if token == t['token']:
                        # 上传
                        print(t['title'], t['description'], t['keywords'])
                        submitter(token_url, title=t['title'], description=t['description'], keyword=t['keywords'],
                                  page_language=t['language'])
                        break

        else:

            for customized_token in customized_tokens:
                if '{0}' in customized_token['token']:
                    title = customized_token['title'].replace('{token}', token)
                    description = customized_token['description'].replace('{token}', token)
                    keywords = customized_token['keywords'].replace('{token}', token)

                    # 检测是否已经存在
                    token_url = price_base_url + token
                    # 检测是否已经存在
                    item = queryTDKStatus(token_url)
                    # 删除老的
                    if item is not None:
                        id = item['id']
                        originalUrl = item['originalUrl']
                        print(originalUrl, id)
                        # 删除之前的
                        # 只删除那个URL全满足的
                        if originalUrl == token_url:
                            deleter(id)

                    # 再次检测
                    item = queryTDKStatus(token_url)

                    if item is None:
                        # 上传
                        submitter(token_url, title=title, description=description, keyword=keywords,
                                  page_language=language)


updater()


def read_excel_into_database(language_code):
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/temp/TDK_ Price Pages [FR & ES].xlsx'
    if os.path.exists(file_path):
        df_data = pandas.read_excel(file_path, sheet_name='PT')
        if df_data.empty:
            raise ValueError('No Data found')
        else:
            # fill na cell with empty string
            __for_NAN__ = 0
            df_data = df_data.dropna(how='all').fillna(__for_NAN__)
            # strip strings of dataframe
            df_str = df_data.select_dtypes(['object'])
            df_data[df_str.columns] = df_str.apply(lambda x: x.str.strip())
            # remove duplicates by column "URL"
            df_duplicated = df_data.duplicated(subset=['URL'], keep=False)
            df_duplicated_data = df_data[df_duplicated]
            df_duplicated_by_website = df_duplicated_data['URL'].to_json()
            if df_duplicated_by_website:
                print(df_duplicated_by_website)
            # 去除重复【URL】
            df_data = df_data.drop_duplicates(subset=['URL'], keep="last")
            df_data = df_data.sort_index()

            # 入库
            dh = database_handler()

            for idx in df_data.index:
                url = ''
                if 'URL' in df_data:
                    url: str = df_data['URL'][idx]

                if 'kucoin.com' not in url:
                    continue

                title = ''
                if 'Title' in df_data:
                    title: str = df_data['Title'][idx]
                if len(title.strip()) < 1:
                    continue
                description = ''
                if 'Description' in df_data:
                    description: str = df_data['Description'][idx]

                if len(description.strip()) < 1:
                    continue

                keywords = ''
                if 'Keywords' in df_data:
                    keywords: str = df_data['Keywords'][idx]

                if len(keywords.strip()) < 1:
                    continue
                print(f'''URL is {url}, title is {title}, description is {description},keywords is {keywords}''')

                dh.save_tdk_table(language_code=language_code, base_url='https://www.kucoin.com/pt/price/', url=url,
                                  title=title,
                                  description=description, keywords=keywords)


# read_tdks_from_database()
# read_excel_into_database(language_code='pt_PT')
