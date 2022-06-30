import json
import os
from db_handler import database_handler
from bs4 import BeautifulSoup
import os
import pathlib
import re
from browser.useragent import ran_user_agent_desktop
from db_handler import database_handler
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement
from typing import List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver as seDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.utils import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
import lxml.html
import lxml.html.clean

#
#
# # temp_location = os.path.dirname(os.path.abspath(__file__)) + "/temp/temp.html"
# # print(temp_location)
#
#
# # dh = database_handler()
# # results = dh.read_article_content_urls()
# # urls = []
# # for result in results:
# #     urls.append(result[0])
# #
# # res = dh.read_article_source_code_except_urls(urls)
# # print(res)
# def initialize_driver() -> WebDriver:
#     driver_options = seDriver.ChromeOptions()
#     """开启无头与否"""
#     # 修改 UA 信息
#     ua_string = ran_user_agent_desktop()
#     driver_options.add_argument(f"--user-agent={ua_string}")
#     driver_options.add_experimental_option('prefs', {'intl.accept_languages': "en-GB"})
#     # 设置无头浏览器
#     driver_options.add_argument('--headless')
#     driver_options.add_argument('--disable-gpu')
#
#     # 配置chrome 浏览器
#     s = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
#     driver = seDriver.Chrome(service=s, options=driver_options)
#     return driver
#
#
#
# def replaceHtmlTag(source_code: str):
#     soup = BeautifulSoup(source_code, 'html.parser')
#     tags = soup.findAll()
#     tags.reverse()
#
#     for tag in tags:
#         if tag.string:
#             tag.string.replace_with(f" {tag.string} ")
#             tag.text.replace(" ", ' ')
#             tag.text.replace("\n", " ").replace("\r", " ").replace("\r\n", " ")
#             tag.text.replace(" ", ' ')
#             tag.text.replace(u"\xa0", ' ')
#             tag.text.replace("&nbsp;", ' ')
#             tag.text.replace(u"\u2022", " ")
#     source_code = str(soup)
#
#     return source_code
#
#
# def removeHtmlTag(selectors: List[str], source_code: str):
#     for selector in selectors:
#         soup = BeautifulSoup(source_code, 'html.parser')
#         tags = soup.select(selector)
#         tags.reverse()
#         for tag in tags:
#             tag.extract()
#         source_code = str(soup)
#     return source_code
#
#
# code = replaceHtmlTag(source_code)
#
# code = removeHtmlTag(['a'], source_code)
# code = code.replace(' ', ' ')
# print(code)
#
# dh = database_handler()
# rs: List[str] = dh.read_anchors_conflict_url_words('BTC')
# for r in rs:
#     print(r[3])
#     r = r[3].replace('[', '').replace(']', '').replace("\"", "").split(',')
#     print(r)


text = '''Before answering this question, we must first understand what wrapped bitcoin is. Wrapped bitcoin is a  token issued based on the Ethereum ERC-20 standard. It aims to bring the liquidity and stability of Bitcoin as a cryptocurrency into the Ethereum ecosystem. Thereby increasing the use cases of Bitcoin, such as participating in liquidity mining of ethereum ecosystem projects with wrapped bitcoin.

Every single wrapped bitcoin issued must be backed by Bitcoin. Each Bitcoin stored by the authorized merchant can correspond to one wrapped bitcoin issued and can be audited on the chain.

For users they can only purchase -wrapped bitcoin or do a 1:1 swap with an authorized merchant. And those merchants mint the wrapped bitcoin from the smart contract and then send an equal amount of Bitcoin as a collateral to the custodian. When someone wants to exchange wrapped bitcoin for Bitcoin, the wrapped bitcoin will be burned on the Ethereum.

To put it simply, one wrapped bitcoin equals one BTC, and the value of BTC can be migrated to the Ethereum ecosystem via wrapped bitcoin. What’s more, wrapped bitcoin has its unique superiority. As an ERC-20 token, the transaction speed of wrapped bitcoin is faster than Bitcoin, and the prime advantage of wrapped bitcoin lies in its integration into Ethereum wallets, dapps and smart contracts.
2btc btcchina btc-usdt btc/usdt btc btc,
According to the last   data   from CoinMarketCap, the total Market Cap of wrapped bitcoin reached $4 billion, the 24H trading volume exceeded $131 million. At the time of writing this article, there have been more than 110,771 WBTC in circulation, and it is increasing.'''.lower()
# # anchor = 'The Crypto Prophecies'.lower()
# anchor = 'Wrapped Bitcoin'.lower()
# # conflicted_symbol = fr'\w{anchor}\s'
# # conflicted_symbol = fr'\s{anchor}'
# # conflicted_symbol = fr'{anchor}\s'
# # conflicted_symbol = fr'{anchor}\w'
# re_ = fr'(?:[\w|\-|\/]*){anchor}(?:[\w|\-|\/]*)'
# conflict_words = re.findall(re_, text)
# for conflict_word in conflict_words:
#     if not conflict_word.strip().lower() == anchor.strip().lower():
#         print(conflict_word.strip().lower())
# dh = database_handler()
# dh.create_anchors_conflict_url_words_table()
print(text)

print("====================")

text = text.encode("utf-8").decode()

determiner = [' ', ',']
target = 'btc'
for a in list(re.finditer(target, text)):
    if text[a.start() - 1] in determiner and text[a.end() + 1] in determiner:
        print(f"{text[a.start():a.end()]} OK")
    else:
        print(f"{text[a.start() - 1:a.end() + 1]} Skip")
