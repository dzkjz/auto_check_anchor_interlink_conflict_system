import requests
import json
from typing import List

language_list = [
    '/de',
    '/es',
    '/fr',
    '/ko',
    '/nl',
    '/pt',
    '/tr',
    '/vi',
    '/zh-hans',
    '/zh-hant',
    '/it',
    '/id',
    '/ms',
    '/hi',
    '/th',
    '/ja',
    '/bn',
    '/pl',
    '/fil',
    '/ru',
]


def submit_bing(urls: List[str]):
    API = "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={apikey}"
    API_KEY = "86e3d4d198fa4dbcaf5d299251013284"  # API密钥

    data = {
        "siteUrl": "https://www.kucoin.com",  # 你在bing webmaster tools里添加的网站 例：https://www.perfcode.com
        "urlList": urls  # 你要提交的URL
    }

    response = requests.post(API.format(apikey=API_KEY), json=data)
    if response.status_code == 200:
        print("提交成功")
    else:
        # 失败
        print(response.status_code)
        print(response.text)


spot_response = requests.get(
    'https://www.kucoin.com/_api_robot/cloudx-scheduler/v1/symbol/symbols?lang=en_US&_ts=1660184050041')
spot_content = spot_response.json()
spot_datas = spot_content['data']
spot_urls = []
for spot_data in spot_datas:
    url = f"https://www.kucoin.com/trading-bot/spot/grid/{spot_data['code']}"
    spot_urls.append(url)
    for lang in language_list:
        url = f"https://www.kucoin.com{lang}/trading-bot/spot/grid/{spot_data['code']}"
        spot_urls.append(url)

futures_response = requests.get(
    'https://www.kucoin.com/_api_robot/cloudx-scheduler/v1/symbol/futures/symbols?allSymbol=1&lang=en_US&_ts=1660184050041')
futures_content = futures_response.json()
futures_datas = futures_content['data']['USDT']
futures_urls = []
for futures_data in futures_datas:
    url = f"https://www.kucoin.com/trading-bot/futures/grid/{futures_data['symbolCode']}"
    futures_urls.append(url)
    for lang in language_list:
        url = f"https://www.kucoin.com{lang}/trading-bot/futures/grid/{futures_data['symbolCode']}"
        futures_urls.append(url)

print(len(spot_urls))
print(len(futures_urls))
# urls = []
# # urls.extend(spot_urls)
# urls.extend(futures_urls)
# # submit urls to bing 500 per request
# while len(urls) > 0:
#     count = 499 if len(urls) > 499 else len(urls)
#     url_spilt = urls[:count]
#     del urls[:count]
#     # print(url_spilt)
#     submit_bing(url_spilt)
